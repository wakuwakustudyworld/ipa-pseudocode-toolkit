from ipa_pseudocode.core.array import Array

stackPos = 3
stack = Array.from_literal([4, 3, None, None])

def push(inputData):
    global stack
    global stackPos
    if stackPos <= len(stack):
        stack[stackPos] = inputData
        stackPos = stackPos + 1
        return True
    else:
        return False

def pop():
    global stack
    global stackPos
    popData = None
    if stackPos > 1:
        stackPos = stackPos - 1
        popData = stack[stackPos]
        stack[stackPos] = None
    return popData
