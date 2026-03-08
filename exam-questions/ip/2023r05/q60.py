from ipa_pseudocode.core.array import Array

def printArray():
    n = None
    m = None
    integerArray = Array.from_literal([2, 4, 1, 3])
    for n in range(1, len(integerArray) - 1 + 1):
        for m in range(1, len(integerArray) - n + 1):
            if integerArray[m] > integerArray[m + 1]:
                integerArray[m], integerArray[m + 1] = integerArray[m + 1], integerArray[m]
    print(*integerArray, sep=',')  # 手動変換: 全要素をコンマ区切りで出力

