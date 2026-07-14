"""
Pure-Python MD4 implementation.
Fallback for systems where hashlib doesn't provide MD4
(e.g. FIPS-enabled Windows, some Python distributions).
"""

import struct

# MD4 constants
A0 = 0x67452301
B0 = 0xEFCDAB89
C0 = 0x98BADCFE
D0 = 0x10325476

_T = lambda x: x & 0xFFFFFFFF

def _F(x, y, z): return _T((x & y) | ((~x) & z))
def _G(x, y, z): return _T((x & y) | (x & z) | (y & z))
def _H(x, y, z): return _T(x ^ y ^ z)

def _rotl(x, n): return _T((x << n) | (x >> (32 - n)))

def _ff(a, b, c, d, x, s):
    return _T(_rotl(_T(a + _F(b, c, d) + x), s))

def _gg(a, b, c, d, x, s):
    return _T(_rotl(_T(a + _G(b, c, d) + x + 0x5A827999), s))

def _hh(a, b, c, d, x, s):
    return _T(_rotl(_T(a + _H(b, c, d) + x + 0x6ED9EBA1), s))

def md4(data: bytes) -> str:
    """Compute MD4 hash of *data* and return hex digest string."""
    # Pre-processing: pad message
    msg = bytearray(data)
    msg_len_bits = len(data) * 8
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0x00)
    msg += struct.pack('<Q', msg_len_bits & 0xFFFFFFFFFFFFFFFF)

    a, b, c, d = A0, B0, C0, D0

    # Process each 512-bit (64-byte) block
    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        x = struct.unpack('<16I', block)

        aa, bb, cc, dd = a, b, c, d

        # Round 1
        a = _ff(a, b, c, d, x[ 0],  3)
        d = _ff(d, a, b, c, x[ 1],  7)
        c = _ff(c, d, a, b, x[ 2], 11)
        b = _ff(b, c, d, a, x[ 3], 19)
        a = _ff(a, b, c, d, x[ 4],  3)
        d = _ff(d, a, b, c, x[ 5],  7)
        c = _ff(c, d, a, b, x[ 6], 11)
        b = _ff(b, c, d, a, x[ 7], 19)
        a = _ff(a, b, c, d, x[ 8],  3)
        d = _ff(d, a, b, c, x[ 9],  7)
        c = _ff(c, d, a, b, x[10], 11)
        b = _ff(b, c, d, a, x[11], 19)
        a = _ff(a, b, c, d, x[12],  3)
        d = _ff(d, a, b, c, x[13],  7)
        c = _ff(c, d, a, b, x[14], 11)
        b = _ff(b, c, d, a, x[15], 19)

        # Round 2
        a = _gg(a, b, c, d, x[ 0],  3)
        d = _gg(d, a, b, c, x[ 4],  5)
        c = _gg(c, d, a, b, x[ 8],  9)
        b = _gg(b, c, d, a, x[12], 13)
        a = _gg(a, b, c, d, x[ 1],  3)
        d = _gg(d, a, b, c, x[ 5],  5)
        c = _gg(c, d, a, b, x[ 9],  9)
        b = _gg(b, c, d, a, x[13], 13)
        a = _gg(a, b, c, d, x[ 2],  3)
        d = _gg(d, a, b, c, x[ 6],  5)
        c = _gg(c, d, a, b, x[10],  9)
        b = _gg(b, c, d, a, x[14], 13)
        a = _gg(a, b, c, d, x[ 3],  3)
        d = _gg(d, a, b, c, x[ 7],  5)
        c = _gg(c, d, a, b, x[11],  9)
        b = _gg(b, c, d, a, x[15], 13)

        # Round 3
        a = _hh(a, b, c, d, x[ 0],  3)
        d = _hh(d, a, b, c, x[ 8],  9)
        c = _hh(c, d, a, b, x[ 4], 11)
        b = _hh(b, c, d, a, x[12], 15)
        a = _hh(a, b, c, d, x[ 2],  3)
        d = _hh(d, a, b, c, x[10],  9)
        c = _hh(c, d, a, b, x[ 6], 11)
        b = _hh(b, c, d, a, x[14], 15)
        a = _hh(a, b, c, d, x[ 1],  3)
        d = _hh(d, a, b, c, x[ 9],  9)
        c = _hh(c, d, a, b, x[ 5], 11)
        b = _hh(b, c, d, a, x[13], 15)
        a = _hh(a, b, c, d, x[ 3],  3)
        d = _hh(d, a, b, c, x[11],  9)
        c = _hh(c, d, a, b, x[ 7], 11)
        b = _hh(b, c, d, a, x[15], 15)

        a = _T(a + aa)
        b = _T(b + bb)
        c = _T(c + cc)
        d = _T(d + dd)

    return struct.pack('<4I', a, b, c, d).hex()
