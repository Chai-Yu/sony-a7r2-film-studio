#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original diagnostic tooling only; third-party rights remain separate. See LICENSING.md and NOTICE.
"""Sample the camera app's threads from the outside while a freeze is reproduced.

The camera has no touch screen and its keys do not go through Android's input
system, so adb cannot press MENU for you: the freeze has to be triggered by
hand. This watches from the outside instead.

Every interval it records, in one adb round trip:

* every thread of the app (state, CPU time, kernel wait channel)
* the process totals (thread count, RSS)
* how many lines the streamed log has produced

A thread that sits in state D (uninterruptible sleep) is blocked inside the
kernel or a native call, which is what a wedged camera looks like from here: the
UI stops responding while the live view, rendered by another pipeline, keeps
running. Such a sample is marked SUSPECT and gets a full snapshot, so a hang can
be diagnosed without a power cycle (which wipes the log buffer).

Usage:
  python tools/freeze_watch.py --serial 192.0.2.10:5555 --log-file build-local/diagnosis/stream.txt
"""

import argparse
import datetime
import pathlib
import subprocess
import sys
import time

DEFAULT_PACKAGE = 'com.yuki.imaging.app.pictureeffectplus'
SAMPLE = ('cat /proc/{pid}/status; echo ===THREADS===; '
          'for t in /proc/{pid}/task/*; do echo "##$t"; cat $t/stat 2>/dev/null; '
          'cat $t/wchan 2>/dev/null; echo; done')

# /proc/<pid>/task/<tid>/stat: the command name may contain spaces and
# parentheses, so only the fields after the last ')' are parsed.  Field 0 is the
# state, fields 11 and 12 are the user and system CPU jiffies.
def parse_stat(line, tid):
    """(state, cumulative CPU jiffies) of one thread stat line."""
    fields = line.rsplit(')', 1)[-1].split()
    if len(fields) < 13:
        return None
    return fields[0], int(fields[11]) + int(fields[12])


def adb(adb_bin, serial, *args, timeout=60):
    result = subprocess.run([adb_bin, '-s', serial, *args], capture_output=True,
                            timeout=timeout, encoding='utf-8', errors='replace')
    return result.stdout or ''


def find_pid(adb_bin, serial, package):
    for line in adb(adb_bin, serial, 'shell', 'ps').splitlines():
        if package in line:
            parts = line.split()
            for index, part in enumerate(parts):
                if part.isdigit() and index:
                    return part
    return None


def sample(adb_bin, serial, pid):
    """(threads, status_lines) with threads = [(tid, state, cpu, wchan), ...]."""
    raw = adb(adb_bin, serial, 'shell', SAMPLE.format(pid=pid))
    status, threads = [], []
    body = raw.split('===THREADS===', 1)
    status = [line for line in body[0].splitlines() if line.strip()]
    for block in body[1].split('##') if len(body) > 1 else []:
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        path, rest = lines[0].strip(), lines[1:]
        tid = path.rsplit('/', 1)[-1]
        stat = next((line for line in rest if line.strip().startswith(tid + ' (')), '')
        wchan = next((line for line in rest if not line.startswith(tid + ' (')), '')
        parsed = parse_stat(stat, tid) if stat else None
        if parsed:
            threads.append((tid, parsed[0], parsed[1], wchan.strip()))
    return threads, status


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--serial', required=True, help='adb serial, e.g. CAMERA_IP:5555')
    ap.add_argument('--adb', default='adb', help='adb executable (default: from PATH)')
    ap.add_argument('--package', default=DEFAULT_PACKAGE)
    ap.add_argument('--interval', type=float, default=2.5, help='seconds between samples')
    ap.add_argument('--samples', type=int, default=0, help='stop after N samples (0: run until Ctrl+C)')
    ap.add_argument('--log-file', type=pathlib.Path,
                    help='streamed logcat file; its line count is recorded so a silent '
                         'app can be told apart from a quiet one')
    ap.add_argument('--out', type=pathlib.Path, default=pathlib.Path('build-local/diagnosis/freeze-watch.txt'))
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out = args.out.open('w', encoding='utf-8')
    previous = {}
    suspect = 0
    print(f'sampling {args.package} every {args.interval}s -> {args.out}', file=sys.stderr)
    print('start the app and press MENU until it freezes; do NOT power off.', file=sys.stderr)

    count = 0
    try:
        while True:
            count += 1
            now = datetime.datetime.now().strftime('%H:%M:%S')
            pid = find_pid(args.adb, args.serial, args.package)
            log_lines = len(args.log_file.read_text(encoding='utf-8', errors='replace').splitlines()) \
                if args.log_file and args.log_file.exists() else -1
            if not pid:
                print(f'{now} app not running (log lines={log_lines})', file=out, flush=True)
            else:
                threads, status = sample(args.adb, args.serial, pid)
                total = sum(cpu for _, _, cpu, _ in threads)
                memory = next((line.split(':', 1)[1].strip() for line in status
                               if line.startswith('VmRSS:')), '?')
                blocked = [f'{tid}:{chan}' for tid, state, _, chan in threads if state == 'D']
                running = [tid for tid, state, _, _ in threads if state == 'R']
                delta = total - sum(previous.values()) if previous else total
                line = (f'{now} pid={pid} threads={len(threads)} rss={memory} '
                        f'cpu_delta={delta}')
                if blocked:
                    line += f' BLOCKED={blocked}'
                if running:
                    line += f' running={running}'
                print(line, file=out, flush=True)
                # A thread in D is blocked inside the kernel or a native call,
                # which is what a wedged camera looks like from the outside: the
                # UI is gone while the live view, on another pipeline, still runs.
                if blocked:
                    suspect += 1
                    print(f'--- SUSPECT SNAPSHOT {now} (threads in D: {len(blocked)}) ---', file=out)
                    for tid, state, cpu, chan in sorted(threads, key=lambda t: -t[2]):
                        print(f'    tid={tid:<7} state={state} cpu={cpu:<7} '
                              f'wchan={chan or "-"}', file=out)
                    print('    status:', file=out)
                    for line in status:
                        if line.startswith(('Threads:', 'VmRSS:', 'Name:')):
                            print('      ', line, file=out)
                    if args.log_file and args.log_file.exists():
                        tail = args.log_file.read_text(encoding='utf-8',
                                                       errors='replace').splitlines()[-40:]
                        print('    log tail:', file=out)
                        for line in tail:
                            print('      ', line[:160], file=out)
                    print(f'--- END SNAPSHOT {now} ---', file=out, flush=True)
                previous = {tid: cpu for tid, _, cpu, _ in threads}
            if args.samples and count >= args.samples:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        out.close()
        print(f'wrote {args.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
