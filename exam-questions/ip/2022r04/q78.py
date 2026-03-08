def checkDigit(originalDigit):
    i = None
    j = None
    k = None
    j = 0
    for i in range(1, len(originalDigit) + 1):
        j = j + originalDigit[i]
    while j > 9:
        k = j // 10
        j = k + (j - 10 * k)
    return j

