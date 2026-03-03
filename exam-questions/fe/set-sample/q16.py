from ipa_pseudocode.core.array import Array

def encode(codePoint):
    utf8Bytes = Array.from_literal([224, 128, 128])
    cp = codePoint
    i = None
    for i in range(len(utf8Bytes), 1 - 1, -1):
        utf8Bytes[i] = utf8Bytes[i] + cp % 64
        cp = cp // 64
    return utf8Bytes
