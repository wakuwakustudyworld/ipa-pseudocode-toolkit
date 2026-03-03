from ipa_pseudocode.core.array import Array

def findPrimeNumbers(maxNum):
    pnList = Array.from_literal([])
    i = None
    j = None
    divideFlag = None
    for i in range(2, maxNum + 1):
        divideFlag = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                divideFlag = False
                break
        if divideFlag == True:
            pnList.append(i)
    return pnList
