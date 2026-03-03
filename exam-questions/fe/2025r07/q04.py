from ipa_pseudocode.core.array import Array

def search(data, key):
    i = None
    j = None
    lenData = None
    lenKey = None
    result = Array.from_literal([])
    lenData = len(data)
    lenKey = len(key)
    for i in range(1, lenData - lenKey + 1 + 1):
        for j in range(1, lenKey + 1):
            if data[i + j - 1] == key[j]:
                if j == lenKey:
                    result.append(i)
            else:
                break
    return result
