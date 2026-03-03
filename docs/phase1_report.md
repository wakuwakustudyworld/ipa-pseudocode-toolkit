# Phase 1 実装レポート

## 概要

Phase 1 では、IPA擬似言語ツールキットの基盤となる以下の機能を実装した。

- 中核データ構造（1-based配列、型定義、文字列操作）
- 字句解析器（レクサー）
- 構文解析器（パーサー）
- 擬似言語 → Python 変換器（トランスレータ）
- 公開API（`parse()`, `translate()`）

対応仕様: IPA「試験で使用する情報技術に関する用語・プログラム言語など」Ver.5.1（2024年4月試験から適用）

- 別紙1: ITパスポート試験用
- 別紙2: 基本情報技術者試験，応用情報技術者試験用

---

## 実装構成

### ファイル一覧

```
src/ipa_pseudocode/           （2,371行）
├── __init__.py                # 公開API: parse(), translate()
├── core/
│   ├── __init__.py
│   ├── types.py               # IPAType列挙型、TypeInfo、parse_type_annotation()
│   ├── array.py               # Array（1-based配列）、Array2D（1-based二次元配列）
│   └── string.py              # char_at()、str_length()
├── parser/
│   ├── __init__.py
│   ├── tokens.py              # TokenType列挙型、Token、KEYWORDS辞書、SYMBOL_OPERATORS
│   ├── lexer.py               # Lexerクラス、tokenize()
│   ├── ast_nodes.py           # 25種類以上のASTノード定義
│   └── grammar.py             # Parserクラス、ExpressionParserクラス、parse()
├── translator/
│   ├── __init__.py
│   ├── codegen.py             # CodeBuilder（インデント管理・コード生成）
│   └── pseudo_to_python.py    # PseudoToPythonTranslator、translate()
└── utils/
    └── __init__.py

tests/                         （1,392行）
├── conftest.py
├── test_array.py              # Array/Array2Dクラスのテスト
├── test_types.py              # 型定義のテスト
├── test_lexer.py              # 字句解析器のテスト
├── test_parser.py             # 構文解析器のテスト
├── test_translator.py         # 変換器のテスト
└── test_integration.py        # 統合テスト（擬似言語→Python→実行→結果検証）
```

### 公開API

```python
import ipa_pseudocode

# 擬似言語 → Python変換
python_code = ipa_pseudocode.translate(source)

# 擬似言語 → AST
program = ipa_pseudocode.parse(source)
```

---

## モジュール詳細

### core/types.py — 型定義

IPA擬似言語の5つの基本型と型注釈パーサーを提供する。

| 擬似言語の型名 | IPAType列挙値 | Pythonの型 |
|-------------|-------------|----------|
| 整数型       | INTEGER     | int      |
| 実数型       | REAL        | float    |
| 文字列型     | STRING      | str      |
| 文字型       | CHAR        | str      |
| 論理型       | BOOLEAN     | bool     |

`parse_type_annotation()` は以下の形式を解析する:

- `"整数型"` → 単純型
- `"整数型の配列"` → 一次元配列
- `"整数型の二次元配列"` → 二次元配列
- `"整数型配列の配列"` → 配列の配列
- `"ListElement"` → カスタム型（クラス名）

### core/array.py — 1-based配列

`Array` クラスと `Array2D` クラスを提供する。IPA擬似言語の添字は1から始まるため、内部でPythonの0-basedリストとの変換を行う。

```python
arr = Array(5, init=0)     # 要素数5、初期値0
arr[1] = 10                # 添字1に代入
arr[0]                     # IndexError: 添字が範囲外です

arr2d = Array2D(3, 4, init=0)  # 3行4列
arr2d[1, 2] = 42               # 1行2列に代入
```

### parser/tokens.py — トークン定義

50種類のトークン型を `TokenType` 列挙型で定義。全角/半角両対応の演算子マッピングを含む。

対応する記号演算子:
- 代入: `←`
- 算術: `＋`/`+`, `−`/`-`, `×`, `÷`
- 関係: `＝`/`=`, `≠`, `＜`/`<`, `＞`/`>`, `≦`, `≧`
- ビット: `∧`, `∨`, `<<`, `>>`
- 宣言: `○`（関数定義マーカー）
- 区切り: `，`/`,`, `：`/`:`

### parser/lexer.py — 字句解析器

文字単位のスキャナで、以下を処理する:

- 空白文字（半角スペース、タブ、全角スペース）のスキップ
- コメント（`/* ... */` ブロックコメント、`// ...` 行コメント）
- 文字列リテラル（ASCII `"..."` およびUnicode `\u201c...\u201d`）
- 数値リテラル（整数・実数）
- Unicode記号演算子の認識
- 日本語識別子（ひらがな、カタカナ、CJK漢字に対応）
- 英字キーワードの大文字小文字不問マッチ

### parser/ast_nodes.py — ASTノード

`dataclass` ベースで25種類以上のノードを定義:

**式（Expression）:**
IntegerLiteral, RealLiteral, StringLiteral, BooleanLiteral, UndefinedLiteral, NegativeInfinity, Identifier, ArrayLiteral, ArrayAccess, MemberAccess, FunctionCall, BinaryOp, UnaryOp, PropertyAccess, CharAt, DynamicArrayInit

**文（Statement）:**
VarDecl, Assignment, IfStatement, WhileStatement, DoWhileStatement, ForStatement, ForEachStatement, ReturnStatement, BreakStatement, PrintStatement, SwapStatement, AppendStatement, IncrementStatement, ExpressionStatement

**構造:**
FunctionDef, Parameter, Program, ElseIfClause

### parser/grammar.py — 構文解析器

ハイブリッド解析戦略を採用:

1. **前処理**: ソースコードを行リストに分割し、空行・コメント行を除去
2. **行ベース分類**: 正規表現で各行の種類を判定（関数定義、変数宣言、制御文、日本語アクション等）
3. **再帰下降パーサー**: 制御構造のネスト処理（if/elseif/else/endif, for/endfor, while/endwhile, do/while）
4. **Prattパーサー**: 式の演算子優先順位解析

**演算子優先順位（低→高）:**

| 優先順位 | 演算子 |
|---------|-------|
| 10      | or    |
| 15      | \|（ビットOR） |
| 20      | and   |
| 25      | &（ビットAND） |
| 30      | ==, !=, <, >, <=, >= |
| 35      | <<, >> |
| 40      | +, -  |
| 50      | *, /, % |
| 60      | not, +, - （単項） |
| 70      | ., [], () |

**日本語条件式パターン:**

| 擬似言語 | 変換結果 |
|---------|---------|
| `age が 3 以下` | `age <= 3` |
| `age が 4 以上` | `age >= 4` |
| `x が 9 より小さい` | `x < 9` |
| `x が 9 より大きい` | `x > 9` |
| `x が y と等しい` | `x == y` |
| `x が y と等しくない` | `x != y` |
| `x が 未定義` | `x is None` |
| `x が 未定義でない` | `x is not None` |
| `x が 3 で割り切れる` | `x % 3 == 0` |
| `x が y でない` | `x != y` |

**日本語アクション文パターン:**

| 擬似言語 | ASTノード |
|---------|----------|
| `pnListの末尾にiの値を追加する` | AppendStatement |
| `data[i]とdata[j]の値を入れ替える` | SwapStatement |
| `countの値を1増やす` | IncrementStatement |
| `繰返し処理を終了する` | BreakStatement |
| `"hello"を出力する` | PrintStatement |

**forループ制御記述パターン:**

| 擬似言語 | ASTノード |
|---------|----------|
| `i を 1 から n まで 1 ずつ増やす` | ForStatement(increment) |
| `i を n から 1 まで 1 ずつ減らす` | ForStatement(decrement) |
| `item に list の要素を順に代入する` | ForEachStatement |

### translator/ — 擬似言語→Python変換

`PseudoToPythonTranslator` がASTビジターとしてPythonコードを生成する。`CodeBuilder` がインデント管理を担当。

**主要変換規則:**

| 擬似言語 | Python |
|---------|--------|
| `○整数型: fee(整数型: age)` | `def fee(age):` |
| `整数型: x ← 0` | `x = 0` |
| `整数型の配列: arr ← {1,2,3}` | `arr = [1, 2, 3]` |
| `x ← y` | `x = y` |
| `if (cond) ... elseif ... else ... endif` | `if cond: ... elif ... else:` |
| `while (cond) ... endwhile` | `while cond:` |
| `do ... while (cond)` | `while True: ... if not (cond): break` |
| `for (iを1からnまで1ずつ増やす)` | `for i in range(1, n + 1):` |
| `for (iをnから1まで1ずつ減らす)` | `for i in range(n, 1 - 1, -1):` |
| `for (itemにlistの要素を順に代入する)` | `for item in list:` |
| `return x` | `return x` |
| `未定義` / `未定義の値` | `None` |
| `true` / `false` | `True` / `False` |
| `×` | `*` |
| `÷` | `/` |
| `mod` | `%` |
| `≠` | `!=` |
| `≦`, `≧` | `<=`, `>=` |
| `∧`, `∨` | `&`, `\|` |
| `arrayの要素数` | `len(array)` |
| `binaryのi文字目の文字` | `binary[i - 1]` |
| `の末尾に...を追加する` | `.append(...)` |
| `...の値を入れ替える` | `a, b = b, a` |
| `age が 3 以下` | `age <= 3` |
| `x が 未定義` | `x is None` |
| `not cond` | `not cond` |

---

## テスト結果

### 実行環境

- Python 3.13.5
- pytest 9.0.2
- ruff 0.15.4（リントエラー 0）

### テスト結果サマリー

```
141 passed in 0.07s
```

### テストファイル別の内訳

| テストファイル | テスト数 | 内容 |
|-------------|---------|------|
| test_array.py | 21 | Array/Array2Dクラスの生成・アクセス・境界チェック |
| test_types.py | 15 | 型注釈パース・Python型ヒント生成 |
| test_lexer.py | 27 | トークン化（リテラル・キーワード・演算子・コメント・識別子） |
| test_parser.py | 33 | AST生成（関数定義・変数宣言・制御構造・日本語パターン） |
| test_translator.py | 31 | Python変換（各構文の変換・日本語条件式・アクション文） |
| test_integration.py | 14 | E2E（擬似言語→Python変換→exec実行→結果値検証） |
| **合計** | **141** | |

### 統合テスト一覧

以下のテストでは、擬似言語をPythonに変換し、`exec()` で実行して結果を検証している。

| テスト名 | 検証内容 |
|---------|---------|
| TestFeeFunction | if/elseif/else分岐: `fee(2)==100`, `fee(5)==300`, `fee(15)==500` |
| TestSumFunction | forループ合計: `total(10)==55`, `total(100)==5050` |
| TestMaxFunction | 1-based配列の最大値検索: `findMax([3,7,2,9,1], 5)==9` |
| TestCountdownFunction | デクリメントforループ: `countdown(10)==55` |
| TestWhileLoop | whileループ: `countUp(5)==5`, `countUp(0)==0` |
| TestDoWhileLoop | do-whileループ: `doCount()==5` |
| TestFactorial | 再帰関数: `factorial(5)==120`, `factorial(0)==1` |
| TestModOperator | mod演算: `isEven(4)==1`, `isEven(7)==0` |
| TestBooleanLogic | and複合条件: `inRange(5,1,10)==1`, `inRange(0,1,10)==0` |
| TestGlobalVariable | 大域変数: `getCount()==0` |
| TestPublicAPI | `parse()`, `translate()`, `__version__` |

### 統合テスト例: 入場料金関数

**入力（擬似言語）:**

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

**出力（Python）:**

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

**検証:**

```python
assert fee(2) == 100   # 3歳以下
assert fee(3) == 100   # 3歳以下（境界値）
assert fee(5) == 300   # 4〜9歳
assert fee(9) == 300   # 4〜9歳（境界値）
assert fee(15) == 500  # 10歳以上
```

### 統合テスト例: 階乗（再帰）

**入力（擬似言語）:**

```
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
```

**出力（Python）:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

**検証:**

```python
assert factorial(5) == 120
assert factorial(0) == 1
assert factorial(1) == 1
```

---

## 既知の制限事項

Phase 1 時点での制限:

1. **日本語プロパティアクセス**: `arrayの要素数` 等の日本語プロパティはパーサー内で正規表現マッチを使用しておらず、Prattパーサーの `PropertyAccess` ノード生成は変換器側で `len()` に変換される設計だが、パーサーで日本語プロパティを自動的にASTノード化する機能は未実装。式中に直接書いた場合は識別子として扱われる。
2. **整数除算**: `÷...の商` を整数除算 `//` に変換する機能は未実装。現状 `÷` はすべて実数除算 `/` に変換される。
3. **動的配列初期化**: `{5個の0}`, `{n行m列の0}` のパースは未実装（ASTノード `DynamicArrayInit` は定義済み）。
4. **Python→擬似言語の逆変換**: Phase 3 で実装予定。
5. **擬似言語の直接実行**: Phase 2 で実装予定。
6. **複数関数の相互呼び出し**: 変換後のPythonコードでは関数定義順に出力されるため、前方参照は問題なく動作する。

---

## 次フェーズへの展望

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 1 | core + lexer/parser + 擬似言語→Python変換 | **完了** |
| Phase 2 | executor（擬似言語の直接実行）+ trace | 未着手 |
| Phase 3 | Python→擬似言語の逆変換 | 未着手 |
| Phase 4 | docs整備 + PyPI公開 + exam-questions充実 | 未着手 |
