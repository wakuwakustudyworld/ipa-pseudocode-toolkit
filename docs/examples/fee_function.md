# 変換例: 入場料金計算関数

年齢に応じた入場料金を返す関数。if/elseif/else/endifの分岐と日本語条件式を使用する。

---

## 擬似言語

```
○整数型: fee(整数型: age)
  整数型: ret
  if (age が 3 以下)
    ret ← 100
  elseif (age が 9 以下)
    ret ← 300
  else
    ret ← 500
  endif
  return ret
```

## 変換結果（Python）

```python
def fee(age):
    ret = None
    if age <= 3:
        ret = 100
    elif age <= 9:
        ret = 300
    else:
        ret = 500
    return ret
```

## 変換ポイント

| 擬似言語 | Python | 説明 |
|---------|--------|------|
| `○整数型: fee(整数型: age)` | `def fee(age):` | 型注釈は除去 |
| `整数型: ret` | `ret = None` | 宣言のみは `None` で初期化 |
| `age が 3 以下` | `age <= 3` | 日本語条件式→比較演算子 |
| `ret ← 100` | `ret = 100` | `←` → `=` |
| `elseif` | `elif` | キーワード変換 |
| `endif` | （インデント終了） | ブロック終端は不要 |

## 実行結果

```python
fee(2)  == 100   # 3歳以下
fee(3)  == 100   # 3歳以下（境界値）
fee(5)  == 300   # 4〜9歳
fee(9)  == 300   # 9歳以下（境界値）
fee(15) == 500   # 10歳以上
```

## 使い方

```python
import ipa_pseudocode

source = """
○整数型: fee(整数型: age)
  整数型: ret
  if (age が 3 以下)
    ret ← 100
  elseif (age が 9 以下)
    ret ← 300
  else
    ret ← 500
  endif
  return ret
"""

# Python コードに変換
python_code = ipa_pseudocode.translate(source)
print(python_code)

# 変換後のコードを実行
ns = {}
exec(python_code, ns)
print(ns["fee"](5))  # 300
```
