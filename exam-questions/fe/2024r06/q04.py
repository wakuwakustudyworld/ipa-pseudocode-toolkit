from ipa_pseudocode.core.array import Array

def merge(data1, data2):
    n1 = len(data1)
    n2 = len(data2)
    work = Array(n1 + n2, init=None)
    i = 1
    j = 1
    k = 1
    while i <= n1 and j <= n2:
        if data1[i] <= data2[j]:
            work[k] = data1[i]
            i = i + 1
        else:
            work[k] = data2[j]
            j = j + 1
        k = k + 1
    while i <= n1:
        work[k] = data1[i]
        i = i + 1
        k = k + 1
    while j <= n2:
        work[k] = data2[j]
        j = j + 1
        k = k + 1
    return work
