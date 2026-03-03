def function1(n, m):
    count = 0
    i = None
    for i in range(n, m + 1):
        if i % 4 == 0:
            count = count + 1
    return count

def function2(n, m):
    count = 0
    tempN = n
    i = None
    j = None
    for i in range(1, 3 + 1):
        if tempN % 4 == 0:
            break
        tempN = tempN + 1
    for j in range(tempN, m + 1, 4):
        count = count + 1
    return count
