# 擬似言語 → Python 対応規則

本ドキュメントは、IPA擬似言語からPythonへの変換規則をまとめたものである。

---

## 基本方針

- 擬似言語の1行を可能な限りPythonの1行に対応させる
- 型宣言は変数の初期化（`None` 代入）に変換する
- 1-based配列は `Array` クラスを使用するか、変換後のPythonではそのまま `[]` アクセスとする
- 日本語の条件式・アクション文はPythonの等価な構文に変換する
- エラーメッセージは日本語で出力する（教育用途）

---

## 構造の変換

### 関数定義

```
擬似言語: ○整数型: fee(整数型: age)
Python:   def fee(age):
```

```
擬似言語: ○display(整数型: n)        // 手続き（戻り値なし）
Python:   def display(n):
```

型注釈は変換後のPythonコードには含めない（型情報はASTに保持されている）。

### 変数宣言

```
擬似言語: 整数型: x
Python:   x = None

擬似言語: 整数型: x ← 0
Python:   x = 0

擬似言語: 整数型: x, y, z
Python:   x = None
          y = None
          z = None

擬似言語: 整数型の配列: arr ← {1, 2, 3}
Python:   arr = [1, 2, 3]
```

### 大域変数

```
擬似言語: 大域: 整数型: gCount ← 0
Python:   gCount = 0
```

大域変数はファイルのトップレベルに出力される。

### 代入

```
擬似言語: x ← 42
Python:   x = 42

擬似言語: arr[i] ← x + 1
Python:   arr[i] = x + 1

擬似言語: node.next ← newNode
Python:   node.next = newNode
```

---

## 制御構造の変換

### if / elseif / else / endif

```
擬似言語:                          Python:
  if (条件式1)                       if 条件式1:
    文1                                  文1
  elseif (条件式2)                   elif 条件式2:
    文2                                  文2
  else                               else:
    文3                                  文3
  endif
```

### while / endwhile

```
擬似言語:                          Python:
  while (条件式)                     while 条件式:
    文                                   文
  endwhile
```

### do ... while

Pythonには `do-while` がないため、`while True` + `break` に変換する。

```
擬似言語:                          Python:
  do                                 while True:
    文                                   文
  while (条件式)                         if not (条件式):
                                             break
```

### for（増分）

```
擬似言語: for (i を 1 から n まで 1 ずつ増やす)
Python:   for i in range(1, n + 1):

擬似言語: for (i を 0 から 10 まで 2 ずつ増やす)
Python:   for i in range(0, 10 + 1, 2):
```

`range()` の終了値に `+ 1` を付ける。これは擬似言語のforループが「〜まで」（終了値を含む）であり、Pythonの `range()` が終了値を含まないためである。

### for（減分）

```
擬似言語: for (i を n から 1 まで 1 ずつ減らす)
Python:   for i in range(n, 1 - 1, -1):

擬似言語: for (i を 10 から 0 まで 2 ずつ減らす)
Python:   for i in range(10, 0 - 1, -2):
```

終了値に `- 1` を付けて、擬似言語の「〜まで」（終了値を含む）を実現する。

### for-each

```
擬似言語: for (item に list の要素を順に代入する)
Python:   for item in list:
```

---

## 式の変換

### 算術演算子

| 擬似言語 | Python | 備考 |
|---------|--------|------|
| `＋` / `+` | `+` | 加算 / 文字列結合 |
| `−` / `-` | `-` | 減算 |
| `×` | `*` | 乗算 |
| `÷` | `/` | 除算（実数） |
| `mod` | `%` | 剰余 |

### 関係演算子

| 擬似言語 | Python |
|---------|--------|
| `＝` / `=` | `==` |
| `≠` | `!=` |
| `＜` / `<` | `<` |
| `＞` / `>` | `>` |
| `≦` | `<=` |
| `≧` | `>=` |

### 論理演算子

| 擬似言語 | Python |
|---------|--------|
| `and` | `and` |
| `or` | `or` |
| `not` | `not` |

### ビット演算子

| 擬似言語 | Python |
|---------|--------|
| `∧` | `&` |
| `∨` | `\|` |
| `<<` | `<<` |
| `>>` | `>>` |

### リテラル

| 擬似言語 | Python |
|---------|--------|
| `true` | `True` |
| `false` | `False` |
| `未定義` / `未定義の値` | `None` |
| `−∞` | `float('-inf')` |
| `42` | `42` |
| `3.14` | `3.14` |
| `"hello"` | `'hello'` |

### 配列リテラル

```
擬似言語: {1, 2, 3}
Python:   [1, 2, 3]

擬似言語: {{1, 2}, {3, 4}}
Python:   [[1, 2], [3, 4]]
```

### 配列アクセス

```
擬似言語: arr[i]
Python:   arr[i]

擬似言語: arr[i, j]
Python:   arr[i, j]
```

注意: 擬似言語の配列は1-basedだが、変換後のPythonコードでは添字をそのまま維持する。
`Array` クラスを使用する場合、`Array` が内部で `index - 1` の変換を行う。

### メンバアクセス・関数呼び出し

```
擬似言語: node.next
Python:   node.next

擬似言語: foo(1, 2)
Python:   foo(1, 2)
```

---

## 日本語条件式の変換

### 比較

| 擬似言語 | Python |
|---------|--------|
| `age が 3 以下` | `age <= 3` |
| `age が 4 以上` | `age >= 4` |
| `x が 9 より小さい` | `x < 9` |
| `x が 9 より大きい` | `x > 9` |
| `x が y と等しい` | `x == y` |
| `x が y と等しくない` | `x != y` |
| `x が y でない` | `x != y` |

### 未定義チェック

| 擬似言語 | Python |
|---------|--------|
| `listHead が 未定義` | `listHead is None` |
| `listHead が 未定義でない` | `listHead is not None` |

`is` / `is not` を使用する（`==` / `!=` ではなく）。

### 割り切れる

| 擬似言語 | Python |
|---------|--------|
| `n が 3 で割り切れる` | `n % 3 == 0` |

### 複合条件

```
擬似言語: age が 1 以上 and age が 10 以下
Python:   age >= 1 and age <= 10
```

`and` / `or` をトップレベルで分割し、各部分を再帰的に解析する。

---

## 日本語アクション文の変換

### 末尾追加

```
擬似言語: pnListの末尾にiの値を追加する
Python:   pnList.append(i)
```

### 値の入れ替え

```
擬似言語: data[i]とdata[j]の値を入れ替える
Python:   data[i], data[j] = data[j], data[i]
```

### 値の増減

```
擬似言語: countの値を1増やす
Python:   count += 1

擬似言語: countの値を1減らす    // IncrementStatementのamountが負
Python:   count += -1
```

### 繰返し処理の終了

```
擬似言語: 繰返し処理を終了する
Python:   break
```

### 出力

```
擬似言語: "hello"を出力する
Python:   print('hello')

擬似言語: xの値とyの値をこの順にコンマ区切りで出力する
Python:   print(x, y, sep=",")
```

---

## 日本語プロパティの変換

| 擬似言語 | Python |
|---------|--------|
| `arrayの要素数` | `len(array)` |
| `strの文字数` | `len(str)` |
| `arr2dの行数` | `arr2d.rows` |
| `arr2dの列数` | `arr2d.cols` |

---

## 変換例

### 例1: 入場料金計算

**擬似言語:**

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

**Python:**

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

### 例2: 合計計算（forループ）

**擬似言語:**

```
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
```

**Python:**

```python
def total(n):
    s = 0
    for i in range(1, n + 1):
        s = s + i
    return s
```

### 例3: 階乗（再帰）

**擬似言語:**

```
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
```

**Python:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### 例4: do-whileループ

**擬似言語:**

```
○整数型: doCount()
  整数型: i ← 0
  do
    i ← i ＋ 1
  while (i ＜ 5)
  return i
```

**Python:**

```python
def doCount():
    i = 0
    while True:
        i = i + 1
        if not (i < 5):
            break
    return i
```

### 例5: 偶数判定（mod演算）

**擬似言語:**

```
○整数型: isEven(整数型: n)
  if (n mod 2 ＝ 0)
    return 1
  endif
  return 0
```

**Python:**

```python
def isEven(n):
    if n % 2 == 0:
        return 1
    return 0
```

### 例6: 範囲内判定（複合条件）

**擬似言語:**

```
○整数型: inRange(整数型: x, 整数型: lo, 整数型: hi)
  if (x ≧ lo and x ≦ hi)
    return 1
  endif
  return 0
```

**Python:**

```python
def inRange(x, lo, hi):
    if x >= lo and x <= hi:
        return 1
    return 0
```
