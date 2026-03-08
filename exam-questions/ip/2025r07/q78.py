def calcMod3():
    totalValue = None
    i = None
    totalValue = 0
    for i in range(1, 7 + 1):
        if i % 3 == 0:
            totalValue = totalValue + i
    print(totalValue)

