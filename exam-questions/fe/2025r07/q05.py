# 手動変換: 自然言語を含む擬似言語のため、トランスレータでは変換不可
# 原文の日本語表現を手動でPythonに書き換えた
from ipa_pseudocode.core.array import Array2D

def f(data):
    # 手動変換: 「dataの要素の和」
    t = sum(data[r, c] for r in range(1, data.rows + 1) for c in range(1, data.cols + 1))
    row = data.rows
    col = data.cols
    result = Array2D(row, col, init=None)
    r = None
    c = None
    for r in range(1, row + 1):
        for c in range(1, col + 1):
            # 手動変換: 「dataの行番号rの要素の和 × dataの列番号cの要素の和 ÷ t」
            row_sum = sum(data[r, j] for j in range(1, col + 1))
            col_sum = sum(data[i, c] for i in range(1, row + 1))
            result[r, c] = row_sum * col_sum / t
    return result
