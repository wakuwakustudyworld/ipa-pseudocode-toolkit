def binaryToInteger(binaryStr):
    integerNum = None
    digitNum = None
    exponent = None
    i = None
    integerNum = 0
    for i in range(1, len(binaryStr) + 1):
        digitNum = int(binaryStr[-i])  # 手動変換: 末尾からi番目の文字を整数型に変換した値
        exponent = 2 ** (i - 1)  # 手動変換: 2の(i-1)乗
        integerNum = integerNum + digitNum * exponent
    return integerNum
