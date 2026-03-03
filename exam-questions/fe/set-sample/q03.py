from ipa_pseudocode.core.array import Array

def makeNewArray(in_):
    out = Array.from_literal([])
    i = None
    tail = None
    out.append(in_[1])
    for i in range(2, len(in_) + 1):
        tail = out[len(out)]
        out.append(tail + in_[i])
    return out
