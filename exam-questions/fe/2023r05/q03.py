from ipa_pseudocode.core.array import Array

data = Array.from_literal([2, 1, 3, 5, 4])

def sort(first, last):
    pivot = None
    i = None
    j = None
    pivot = data[(first + last) // 2]
    i = first
    j = last
    while True:
        while data[i] < pivot:
            i = i + 1
        while pivot < data[j]:
            j = j - 1
        if i >= j:
            break
        data[i], data[j] = data[j], data[i]
        i = i + 1
        j = j - 1
    print(*data)  # 手動変換: 「dataの全要素の値を要素番号の順に空白区切りで出力する」
    if first < i - 1:
        sort(first, i - 1)
    if j + 1 < last:
        sort(j + 1, last)
