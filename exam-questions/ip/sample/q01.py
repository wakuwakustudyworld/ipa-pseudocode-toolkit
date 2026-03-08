def calcMean(dataArray):
    sum = None
    mean = None
    i = None
    sum = 0
    for i in range(1, len(dataArray) + 1):
        sum = sum + dataArray[i]
    mean = sum / len(dataArray)
    return mean

