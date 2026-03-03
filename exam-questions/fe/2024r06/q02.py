def convDecimal(binary):
    i = None
    length = None
    result = 0
    length = len(binary)
    for i in range(1, length + 1):
        result = result * 2 + int(binary[i - 1])
    return result
