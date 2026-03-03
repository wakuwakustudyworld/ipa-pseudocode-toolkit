from ipa_pseudocode.core.array import Array

def findRank(sortedData, p):
    i = None
    i = p * (len(sortedData) - 1)
    return sortedData[i + 1]

def summarize(sortedData):
    rankData = Array.from_literal([])
    p = Array.from_literal([0, 0.25, 0.5, 0.75, 1])
    i = None
    for i in range(1, len(p) + 1):
        rankData.append(findRank(sortedData, p[i]))
    return rankData
