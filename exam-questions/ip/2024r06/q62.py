from ipa_pseudocode.core.array import Array


def convert(arrayInput):
    stringOutput = ''
    i = None
    for i in range(1, len(arrayInput) + 1):
        if arrayInput[i] == 1:
            stringOutput += 'A'  # 手動変換: 文字列の末尾に追加
        else:
            stringOutput += 'B'  # 手動変換: 文字列の末尾に追加
    return stringOutput
