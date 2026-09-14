#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Length-changing edits of one string inside a binary AndroidManifest.xml.

apktool decodes with -r, so AndroidManifest.xml in the work directory stays a
binary AXML document instead of becoming text. A plain bytes.replace() is only
safe while the replacement encodes to exactly the same number of bytes: AXML
stores one explicit offset per string plus the pool size and the document size,
so a longer string invalidates every offset that follows it and the manifest
turns into garbage without any error. This module rewrites the pool instead, and
takes the same route for equal-length edits so a single code path is exercised.

Only what this project needs is implemented, and everything else is rejected by
an assertion rather than handled by an untested branch: a UTF-16 string pool
(the manifest from the Sony base APK uses one) without a style table.
"""
import struct

AXML_MAGIC = b'\x03\x00\x08\x00'
TYPE_STRING_POOL = 0x0001
POOL_HEADER = 28
FILE_SIZE_OFFSET = 4
POOL_OFFSET = 8


def _pool(data):
    """Chunk sizes and the string count of the leading string pool."""
    assert data[:4] == AXML_MAGIC, 'not a binary AXML document'
    type_, header, size = struct.unpack_from('<HHI', data, POOL_OFFSET)
    assert type_ == TYPE_STRING_POOL, f'first chunk is 0x{type_:04x}, not a string pool'
    assert header == POOL_HEADER, f'unexpected string pool header size {header}'
    count, styles, flags, strings_start, styles_start = struct.unpack_from(
        '<IIIII', data, POOL_OFFSET + 8)
    assert count, 'empty string pool'
    assert flags == 0, f'only UTF-16 pools are handled, flags=0x{flags:08x}'
    assert styles == 0 and styles_start == 0, 'styled string pools are not handled'
    assert strings_start == POOL_HEADER + 4 * count, (
        f'unexpected stringsStart {strings_start} for {count} strings')
    return size, count, strings_start


def _decode(data, count, strings_start):
    """The strings of the pool, in index order."""
    base = POOL_OFFSET + strings_start
    result = []
    for i in range(count):
        rel = struct.unpack_from('<I', data, POOL_OFFSET + POOL_HEADER + 4 * i)[0]
        start = base + rel
        chars = struct.unpack_from('<H', data, start)[0]
        end = start + 2 + 2 * chars
        assert data[end:end + 2] == b'\x00\x00', f'string {i} is not NUL terminated'
        result.append(data[start + 2:end].decode('utf-16le'))
    return result


def _encode(text):
    """One UTF-16 pool entry: character count, UTF-16 code units, NUL."""
    units = text.encode('utf-16le')
    return struct.pack('<H', len(units) // 2) + units + b'\x00\x00'


def strings(path):
    """Every string in the AndroidManifest at `path`, for verification."""
    data = path.read_bytes()
    size, count, strings_start = _pool(data)
    assert len(data) >= POOL_OFFSET + size, 'string pool runs past the end of the file'
    return _decode(data, count, strings_start)


def replace_string(data, old, new):
    """`data` with the single string pool entry equal to `old` set to `new`.

    `old` must occur exactly once in the pool. The string keeps its index, so
    nothing that references it (attribute values hold indices, not offsets) needs
    to change: only the entries after it move, and their offsets, the pool size
    and the document size are recomputed. The pool keeps its 4-byte alignment.
    """
    size, count, strings_start = _pool(data)
    values = _decode(data, count, strings_start)
    hits = [i for i, value in enumerate(values) if value == old]
    assert len(hits) == 1, f'{old!r} occurs {len(hits)} times in the string pool, expected 1'
    index = hits[0]
    if values[index] == new:
        return data

    # The existing entries must already sit at exactly these offsets: that proves
    # the pool has no gap this rebuild would silently collapse, and therefore that
    # re-encoding the untouched strings reproduces their bytes.
    walked, stored = 0, []
    for value in values:
        stored.append(walked)
        walked += len(_encode(value))
    assert stored == [struct.unpack_from('<I', data, POOL_OFFSET + POOL_HEADER + 4 * i)[0]
                      for i in range(count)], 'string offsets are not tightly packed'
    assert (strings_start + walked + 3) // 4 * 4 == size, (
        f'entries take {walked} bytes, which does not explain a '
        f'{size - strings_start}-byte string area')

    # Rebuild the data area. Only entries after `index` can move.
    encoded = [_encode(new if i == index else value) for i, value in enumerate(values)]
    offsets = []
    position = 0
    for entry in encoded:
        offsets.append(position)
        position += len(entry)

    body = b''.join(encoded)
    pool_size = strings_start + len(body)
    padded = (pool_size + 3) // 4 * 4
    header = struct.pack('<HHIIIIII', TYPE_STRING_POOL, POOL_HEADER, padded,
                         count, 0, 0, strings_start, 0)
    header += struct.pack(f'<{count}I', *offsets)
    assert len(header) == POOL_HEADER + 4 * count
    pool = header + body + b'\x00' * (padded - pool_size)

    rebuilt = data[:POOL_OFFSET] + pool + data[POOL_OFFSET + size:]
    rebuilt = (rebuilt[:FILE_SIZE_OFFSET]
               + struct.pack('<I', len(rebuilt))
               + rebuilt[FILE_SIZE_OFFSET + 4:])
    # A round trip through the rebuilt bytes must reproduce every string.
    assert _decode(rebuilt, count, strings_start) == [
        new if i == index else value for i, value in enumerate(values)]
    return rebuilt
