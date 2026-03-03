# ipa-pseudocode-toolkit

情報処理技術者試験（ITパスポート試験・基本情報技術者試験・応用情報技術者試験）の擬似言語を解析・変換するPythonツールキット。

IPA「試験で使用する情報技術に関する用語・プログラム言語など」[Ver.5.1](https://www.ipa.go.jp/shiken/syllabus/doe3um0000002djj-att/shiken_yougo_ver5_1.pdf)（2024年4月試験から適用）に準拠。

## 特徴

- IPA擬似言語のソースコードをPythonに変換
- 全角演算子（`←`, `×`, `÷`, `≠`, `≦`, `≧` 等）に対応
- 日本語の条件式（`age が 3 以下`）やアクション文（`の末尾に...を追加する`）を解析
- 1-based配列クラス（`Array`, `Array2D`）を提供
- 別紙1（ITパスポート試験用）・別紙2（基本情報・応用情報技術者試験用）の両方に対応

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

| 擬似言語 | Python |
| --------- | -------- |
| `←` | `=` |
| `×` | `*` |
| `÷` | `/` |
| `mod` | `%` |
| `＝` | `==` |
| `≠` | `!=` |
| `≦` | `<=` |
| `≧` | `>=` |
| `∧` | `&` |
| `∨` | `\|` |

### 日本語条件式

| 擬似言語 | Python |
| --------- | -------- |
| `age が 3 以下` | `age <= 3` |
| `age が 4 以上` | `age >= 4` |
| `x が 未定義` | `x is None` |
| `x が 未定義でない` | `x is not None` |
| `n が 3 で割り切れる` | `n % 3 == 0` |
| `x が y と等しい` | `x == y` |

### 日本語アクション文

| 擬似言語 | Python |
| --------- | -------- |
| `pnListの末尾にiの値を追加する` | `pnList.append(i)` |
| `data[i]とdata[j]の値を入れ替える` | `data[i], data[j] = data[j], data[i]` |
| `countの値を1増やす` | `count += 1` |
| `繰返し処理を終了する` | `break` |
| `"hello"を出力する` | `print('hello')` |

## API

### `ipa_pseudocode.translate(source: str) -> str`

擬似言語のソースコードをPythonコードの文字列に変換する。

### `ipa_pseudocode.parse(source: str) -> Program`

擬似言語のソースコードをパースしてAST（抽象構文木）を返す。

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
├── __init__.py          # 公開API: parse(), translate()
├── core/                # 中核データ構造
│   ├── types.py         # 型定義（整数型、実数型、論理型等）
│   ├── array.py         # 1-based配列（Array, Array2D）
│   └── string.py        # 文字列操作ヘルパー
├── parser/              # 擬似言語→AST
│   ├── tokens.py        # トークン定義
│   ├── lexer.py         # 字句解析器
│   ├── ast_nodes.py     # ASTノード定義
│   └── grammar.py       # 構文解析器
└── translator/          # AST→Pythonコード
    ├── codegen.py       # コード生成ヘルパー
    └── pseudo_to_python.py  # Python変換器
```

### ロードマップ

| フェーズ | 内容 | 状態 |
| --------- | ------ | ------ |
| Phase 1 | core + lexer/parser + 擬似言語→Python変換 | 完了 |
| Phase 2 | executor（擬似言語の直接実行）+ trace | 未着手 |
| Phase 3 | Python→擬似言語の逆変換 | 未着手 |
| Phase 4 | docs整備 + PyPI公開 + exam-questions充実 | 未着手 |

## ライセンス

MIT License
