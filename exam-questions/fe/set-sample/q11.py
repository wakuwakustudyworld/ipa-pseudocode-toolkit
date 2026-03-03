from ipa_pseudocode.core.array import Array

def binSort(data):
    n = len(data)
    bins = Array(n, init=None)
    i = None
    for i in range(1, n + 1):
        bins[data[i]] = data[i]
    return bins
