# ipa-pseudocode-toolkit

情報処理技術者試験（ITパスポート試験・基本情報技術者試験・応用情報技術者試験）の擬似言語を解析・変換・実行・トレースするPythonツールキット。

IPA「試験で使用する情報技術に関する用語・プログラム言語など」[Ver.5.1](https://www.ipa.go.jp/shiken/syllabus/doe3um0000002djj-att/shiken_yougo_ver5_1.pdf)（2024年4月試験から適用）に準拠。

## 特徴

- IPA擬似言語のソースコードをPythonに変換（**公開問題49問で100%自動変換達成**）
- 擬似言語を直接実行（Python変換不要）
- 実行過程のトレース表生成（Markdown / CSV出力対応）
- PythonコードからIPA擬似言語への逆変換
- 全角演算子（`←`, `×`, `÷`, `≠`, `≦`, `≧` 等）に対応
- 日本語の条件式（`age が 3 以下`）やアクション文（`の末尾に...を追加する`）を解析
- 複合条件（`かつ` / `または`）、集約関数（要素の和）、集合操作等の高度なパターンに対応
- 1-based配列クラス（`Array`, `Array2D`）を提供
- 別紙1（ITパスポート試験用）・別紙2（基本情報・応用情報技術者試験用）の両方に対応
- IPA公開問題49問の擬似言語とPython変換コードを同梱（`exam-questions/`）

## インストール

```bash
pip install ipa-pseudocode-toolkit
```

開発版を使う場合:

```bash
git clone https://github.com/wakuwakustudyworld/ipa-pseudocode-toolkit.git
cd ipa-pseudocode-toolkit
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 使い方

### 擬似言語をPythonに変換する

```python
import ipa_pseudocode

source = """\
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

# Pythonコードに変換
python_code = ipa_pseudocode.translate(source)
print(python_code)
```

出力:

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

### 変換したコードを実行する

```python
import ipa_pseudocode

source = """\
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
"""

code = ipa_pseudocode.translate(source)
ns = {}
exec(code, ns)

print(ns["factorial"](5))   # 120
print(ns["factorial"](10))  # 3628800
```

### 擬似言語を直接実行する（Python変換不要）

```python
import ipa_pseudocode
from ipa_pseudocode.core.array import Array

source = """\
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
"""

# 関数を指定して呼び出す
result = ipa_pseudocode.call_function(source, "total", 10)
print(result)  # 55
```

### トレース表を生成する

IPA試験のトレース問題の自動解答・解説に活用できる。

```python
import ipa_pseudocode

source = """\
整数型: x ← 1
整数型: y ← 2
整数型: z ← 3
x ← y
y ← z
z ← x
"""

table = ipa_pseudocode.trace(source)
print(table.to_markdown())
```

出力:

```markdown
| Step | 文 | x | y | z | 出力 |
| --- | --- | --- | --- | --- | --- |
| 1 | x ← 1 | 1 | | | |
| 2 | y ← 2 | 1 | 2 | | |
| 3 | z ← 3 | 1 | 2 | 3 | |
| 4 | x ← 2 | 2 | 2 | 3 | |
| 5 | y ← 3 | 2 | 3 | 3 | |
| 6 | z ← 2 | 2 | 3 | 2 | |
```

特定の変数のみ追跡する場合:

```python
table = ipa_pseudocode.trace(source, watch=["x", "y"])
print(table.to_csv())   # CSV形式で出力
```

### PythonコードをIPA擬似言語に逆変換する

```python
import ipa_pseudocode

python_code = """\
def fee(age: int) -> int:
    if age <= 3:
        ret = 100
    elif age <= 9:
        ret = 300
    else:
        ret = 500
    return ret
"""

pseudo_code = ipa_pseudocode.reverse_translate(python_code)
print(pseudo_code)
```

出力:

```
○整数型: fee(整数型: age)
  if (age ≦ 3)
    ret ← 100
  elseif (age ≦ 9)
    ret ← 300
  else
    ret ← 500
  endif
  return ret
```

### ASTを取得する

```python
import ipa_pseudocode

source = """\
○整数型: add(整数型: a, 整数型: b)
  return a ＋ b
"""

program = ipa_pseudocode.parse(source)
func = program.functions[0]
print(func.name)                        # "add"
print(func.return_type)                 # "整数型"
print([p.name for p in func.params])    # ["a", "b"]
```

### 1-based配列を使う

擬似言語の配列は添字が1から始まる。変換後のPythonコードで1-based配列が必要な場合は `Array` クラスを使用する。

```python
from ipa_pseudocode.core.array import Array, Array2D

# 一次元配列
arr = Array.from_literal([10, 20, 30, 40, 50])
print(arr[1])   # 10（1始まり）
print(arr[5])   # 50
print(len(arr)) # 5

# 二次元配列
arr2d = Array2D.from_literal([[1, 2, 3], [4, 5, 6]])
print(arr2d[1, 2])  # 2（1行2列）
print(arr2d[2, 3])  # 6（2行3列）
```

## 対応する擬似言語構文

### 制御構造

| 擬似言語 | 変換後のPython |
| --------- | -------------- |
| `if (条件) ... elseif ... else ... endif` | `if ...: elif ...: else:` |
| `while (条件) ... endwhile` | `while ...:` |
| `do ... while (条件)` | `while True: ... if not (...): break` |
| `for (iを1からnまで1ずつ増やす) ... endfor` | `for i in range(1, n + 1):` |
| `for (iをnから1まで1ずつ減らす) ... endfor` | `for i in range(n, 1 - 1, -1):` |
| `for (itemにlistの要素を順に代入する) ... endfor` | `for item in list:` |

### 演算子

| 擬似言語 | Python | 備考 |
| --------- | -------- | ---- |
| `←` | `=` | 代入 |
| `×` | `*` | 乗算 |
| `÷` | `/` | 実数除算 |
| `÷ Xの商` | `// X` | 整数除算（商） |
| `mod` | `%` | 剰余 |
| `＝` | `==` | 等価 |
| `≠` | `!=` | 非等価 |
| `≦` | `<=` | 以下 |
| `≧` | `>=` | 以上 |
| `∧` | `&` | ビットAND |
| `∨` | `\|` | ビットOR |
| `−` / `－` / `ー` | `-` | 減算（U+2212, U+FF0D, U+30FC 全対応） |

### 日本語条件式

| 擬似言語 | Python |
| --------- | -------- |
| `age が 3 以下` | `age <= 3` |
| `age が 4 以上` | `age >= 4` |
| `t が d 未満` | `t < d` |
| `x が 未定義` | `x is None` |
| `x が 未定義でない` | `x is not None` |
| `n が 3 で割り切れる` | `n % 3 == 0` |
| `x が y と等しい` | `x == y` |
| `A かつ B` | `A and B` |
| `A または B` | `A or B` |
| `orderのいずれかの要素の値がitemの値と等しい` | `any(e == item for e in order)` |

### 日本語アクション文・式パターン

| 擬似言語 | Python |
| --------- | -------- |
| `pnListの末尾にiの値を追加する` | `pnList.append(i)` |
| `stringOutputの末尾に"A"を追加する`（文字列型） | `stringOutput += 'A'` |
| `data[i]とdata[j]の値を入れ替える` | `data[i], data[j] = data[j], data[i]` |
| `countの値を1増やす` | `count += 1` |
| `繰返し処理を終了する` | `break` |
| `"hello"を出力する` | `print('hello')` |
| `dataの全要素の値を空白区切りで出力する` | `print(*data, sep=' ')` |
| `c1の1文字だけから成る文字列` | `str(c1)` |
| `binaryStrの末尾からi番目の文字を整数型に変換した値` | `int(binaryStr[-i])` |
| `2の(i − 1)乗` | `2 ** (i - 1)` |
| `dataの要素の和` | `sum(data)` |
| `dataの行番号rの要素の和` | `sum(data.row(r))` |
| `ordersに含まれる文字列を重複なく辞書順に格納した配列` | `sorted(set(s for sub in orders for s in sub))` |
| `allItemsの複製から値がitemである要素を除いた配列` | `[x for x in allItems if x != item]` |

## API

### `ipa_pseudocode.translate(source: str) -> str`

擬似言語のソースコードをPythonコードの文字列に変換する。

### `ipa_pseudocode.parse(source: str) -> Program`

擬似言語のソースコードをパースしてAST（抽象構文木）を返す。

### `ipa_pseudocode.execute(source: str, trace_enabled: bool = False) -> ExecutionResult`

擬似言語のソースコードを直接実行する。戻り値の `ExecutionResult` には以下が含まれる:
- `output: list[str]` — 出力された文字列のリスト
- `return_value: Any` — トップレベルの戻り値
- `trace: TraceTable | None` — トレース表（`trace_enabled=True` の場合）
- `global_vars: dict[str, Any]` — 実行後のグローバル変数

### `ipa_pseudocode.call_function(source: str, func_name: str, *args) -> Any`

擬似言語で定義された関数を指定引数で呼び出し、戻り値を返す。

### `ipa_pseudocode.trace(source: str, watch: list[str] | None = None) -> TraceTable`

擬似言語を実行し、トレース表を返す。`watch` で特定の変数のみ追跡可能。
`TraceTable` は `.to_markdown()`, `.to_csv()`, `.to_dict()` で出力できる。

### `ipa_pseudocode.reverse_translate(source: str) -> str`

PythonソースコードをIPA擬似言語に逆変換する。
Python の型ヒント（`int`, `str`, `bool` 等）があれば擬似言語の型宣言に変換される。
演算子・制御構造・特殊パターン（swap, append, `+=`, `print`, `len` 等）を自動認識する。

## 公開問題の擬似言語コード

`exam-questions/` に IPA公開問題49問の擬似言語（`.pseudo`）とPython変換コード（`.py`）を収録している。

| 試験区分 | 問題数 | 自動変換 | 問題PDF |
|---------|--------|----------|---------|
| ITパスポート試験（IP） | 10問 | 10/10 (100%) | [公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/questions.html) |
| 基本情報技術者試験（FE） | 35問 | 35/35 (100%) | [公開問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/sg_fe/koukai/index.html) |
| 応用情報技術者試験（AP） | 4問 | 4/4 (100%) | [過去問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/index.html) |
| **合計** | **49問** | **49/49 (100%)** | |

「自動変換」= `ipa_pseudocode.translate()` の出力が `py_compile` を通過すること。

変換精度の改善記録は [docs/translation_improvements.md](docs/translation_improvements.md) を参照。

## 開発

```bash
# テスト実行
python -m pytest tests/ -v

# リントチェック
ruff check src/ tests/
```

### プロジェクト構成

```text
src/ipa_pseudocode/
├── __init__.py          # 公開API: parse(), translate(), reverse_translate(), execute(), call_function(), trace()
├── core/                # 中核データ構造
│   ├── types.py         # 型定義（整数型、実数型、論理型等）
│   ├── array.py         # 1-based配列（Array, Array2D）
│   └── string.py        # 文字列操作ヘルパー
├── parser/              # 擬似言語→AST
│   ├── tokens.py        # トークン定義
│   ├── lexer.py         # 字句解析器
│   ├── ast_nodes.py     # ASTノード定義
│   └── grammar.py       # 構文解析器
├── translator/          # AST⇔コード変換
│   ├── codegen.py       # コード生成ヘルパー
│   ├── pseudo_to_python.py  # 擬似言語→Python変換器
│   └── python_to_pseudo.py  # Python→擬似言語逆変換器
└── runtime/             # 擬似言語の直接実行・トレース
    ├── executor.py      # AST直接実行エンジン
    ├── builtins.py      # 組込み関数
    └── trace.py         # トレース表の記録・出力
```

### ロードマップ

| フェーズ | 内容 | 状態 |
| --------- | ------ | ------ |
| Phase 1 | core + lexer/parser + 擬似言語→Python変換 | 完了 |
| Phase 2 | executor（擬似言語の直接実行）+ trace | 完了 |
| Phase 3 | Python→擬似言語の逆変換 | 完了 |
| Phase 4 | 変換精度改善（78%→100%）+ docs整備 + exam-questions充実 | 完了 |
| Phase 5 | PyPI公開 | 完了 |

## ライセンス

MIT License
