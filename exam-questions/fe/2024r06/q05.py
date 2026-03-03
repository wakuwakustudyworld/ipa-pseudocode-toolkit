# 手動変換: 自然言語を含む擬似言語のため、トランスレータでは変換不可
# 原文の日本語表現を手動でPythonに書き換えた
from ipa_pseudocode.core.array import Array

orders = Array.from_literal([
    Array.from_literal(['A', 'B', 'D']),
    Array.from_literal(['A', 'D']),
    Array.from_literal(['A']),
    Array.from_literal(['A', 'B', 'E']),
    Array.from_literal(['B']),
    Array.from_literal(['C', 'E']),
])

def putRelatedItem(item):
    # 手動変換: 「ordersに含まれる文字列を重複なく辞書順に格納した配列」
    allItems = Array.from_literal(sorted(set(x for order in orders for x in order)))
    # 手動変換: 「allItemsの複製から値がitemである要素を除いた配列」
    otherItems = Array.from_literal([x for x in allItems if x != item])
    i = None
    itemCount = 0
    arrayK = Array(len(otherItems), init=0)
    arrayM = Array(len(otherItems), init=0)
    valueL = None
    maxL = float('-inf')
    order = None
    relatedItem = None
    for order in orders:
        # 手動変換: 「orderのいずれかの要素の値がitemの値と等しい」
        if item in list(order):
            itemCount += 1
        for i in range(1, len(otherItems) + 1):
            # 手動変換: 「orderのいずれかの要素の値がotherItems[i]の値と等しい」
            if otherItems[i] in list(order):
                if item in list(order):
                    arrayM[i] += 1
                arrayK[i] += 1
    for i in range(1, len(otherItems) + 1):
        valueL = arrayM[i] * len(orders) / (itemCount * arrayK[i])
        if valueL > maxL:
            maxL = valueL
            relatedItem = otherItems[i]
    print(relatedItem, maxL, sep=",")
