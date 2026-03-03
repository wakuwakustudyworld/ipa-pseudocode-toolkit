def rev(byte):
    rbyte = byte
    r = 0
    i = None
    for i in range(1, 8 + 1):
        r = r << 1 | rbyte & 1
        rbyte = rbyte >> 1
    return r
