from ipa_pseudocode.core.array import Array

hashArray = None

def add(value):
    global hashArray
    i = calcHash1(value)
    if hashArray[i] == -1:
        hashArray[i] = value
        return True
    else:
        i = calcHash2(value)
        if hashArray[i] == -1:
            hashArray[i] = value
            return True
    return False

def calcHash1(value):
    return value % len(hashArray) + 1

def calcHash2(value):
    return (value + 3) % len(hashArray) + 1

def test():
    global hashArray
    hashArray = Array(5, init=-1)
    add(3)
    add(18)
    add(11)
