from ipa_pseudocode.core.array import Array

array = Array.from_literal([1, 2, 3, 4, 5])
right = None
left = None
tmp = None
for left in range(1, len(array) // 2 + 1):
    right = len(array) - left + 1
    tmp = array[right]
    array[right] = array[left]
    array[left] = tmp
