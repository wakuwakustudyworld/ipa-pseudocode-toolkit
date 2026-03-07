# Phase 3 実装結果: Python → 擬似言語 逆変換

## 概要

Phase 2 で構築した Executor/Trace に続き、**Python ソースコードを IPA 擬似言語に逆変換** する機能を実装した。Python 標準ライブラリの `ast` モジュールでパースし、IPA 擬似言語の構文に変換する。

### 目的

1. **教育用途**: Python で書かれたアルゴリズムを擬似言語で表示し、試験対策に活用
2. **往復変換**: 擬似言語 → Python → 擬似言語 のラウンドトリップで変換の正しさを検証
3. **教材作成**: Python コードから IPA 試験形式の擬似言語問題を自動生成

---

## 実装対象

```
src/ipa_pseudocode/translator/
└── python_to_pseudo.py   # Python → 擬似言語 逆変換器（新規作成）
```

---

## アーキテクチャ

### 変換パイプライン

```
Python ソースコード
    ↓  Python 標準 ast.parse()
Python AST
    ↓  PythonToPseudoTranslator（独自実装）
IPA 擬似言語テキスト
```

Phase 1 の擬似言語 → Python 変換（独自 Lexer → Parser → AST → コード生成）とは異なり、Python 側のパースには標準ライブラリの `ast` モジュールをそのまま使用する。

### クラス設計

```python
class PythonToPseudoTranslator:
    """Python AST → IPA 擬似言語テキスト"""

    def translate(self, source: str) -> str:
        """エントリポイント: Python ソースコード → 擬似言語"""

    # --- 文の変換 ---
    def _translate_function_def(self, node: ast.FunctionDef) -> list[str]
    def _translate_assign(self, node: ast.Assign) -> list[str]
    def _translate_ann_assign(self, node: ast.AnnAssign) -> list[str]
    def _translate_aug_assign(self, node: ast.AugAssign) -> list[str]
    def _translate_if(self, node: ast.If) -> list[str]
    def _translate_while(self, node: ast.While) -> list[str]
    def _translate_for(self, node: ast.For) -> list[str]
    def _translate_return(self, node: ast.Return) -> list[str]
    def _translate_break(self, node: ast.Break) -> list[str]
    def _translate_expr_stmt(self, node: ast.Expr) -> list[str]

    # --- 式の変換 ---
    def _expr(self, node: ast.expr) -> str

    # --- パターン検出 ---
    def _is_do_while(self, node: ast.While) -> tuple[bool, ast.expr | None]
    def _is_swap(self, node: ast.Assign) -> bool
    def _is_range_for(self, node: ast.For) -> tuple[bool, dict]
    def _is_print_call(self, node: ast.Expr) -> bool
    def _is_append_call(self, node: ast.Expr) -> bool
```

---

## 変換規則

### 演算子の変換

| Python | 擬似言語 | 備考 |
|--------|---------|------|
| `+` | `＋` | 加算 |
| `-` | `−` | 減算（U+2212） |
| `*` | `×` | 乗算 |
| `/` | `÷` | 実数除算 |
| `//` | `÷...の商` | 整数除算 |
| `%` | `mod` | 剰余 |
| `==` | `＝` | 等価 |
| `!=` | `≠` | 非等価 |
| `<=` | `≦` | 以下 |
| `>=` | `≧` | 以上 |
| `<` | `＜` | 未満 |
| `>` | `＞` | 超過 |
| `&` | `∧` | ビットAND |
| `\|` | `∨` | ビットOR |

### 型ヒントの変換

| Python 型 | 擬似言語型 |
|-----------|----------|
| `int` | `整数型` |
| `float` | `実数型` |
| `str` | `文字列型` |
| `bool` | `論理型` |
| `list` | `配列型` |

### 制御構造の変換

| Python | 擬似言語 |
|--------|---------|
| `def f(x: int) -> int:` | `○整数型: f(整数型: x)` |
| `if ... : elif ... : else:` | `if (...) ... elseif (...) ... else ... endif` |
| `while cond:` | `while (cond) ... endwhile` |
| `while True: ... if not cond: break` | `do ... while (cond)` |
| `for i in range(1, n+1):` | `for (i を 1 から n まで 1 ずつ増やす)` |
| `for i in range(n, 0, -1):` | `for (i を n から 1 まで 1 ずつ減らす)` |
| `for x in arr:` | `for (x に arr の要素を順に代入する)` |
| `break` | `繰返し処理を終了する` |
| `return expr` | `return expr` |

### 特殊パターンの検出と変換

Phase 1 の擬似言語 → Python 変換で生成される Python パターンを認識し、元の擬似言語表現に復元する。

| Python パターン | 擬似言語 | 検出方法 |
|----------------|---------|---------|
| `a, b = b, a` | `aとbの値を入れ替える` | タプル代入で左右が逆順 |
| `arr.append(val)` | `arrの末尾にvalの値を追加する` | `.append()` メソッド呼び出し |
| `count += 1` | `countの値を1増やす` | `AugAssign(Add)` |
| `count -= 1` | `countの値を1減らす` | `AugAssign(Sub)` |
| `print(x)` | `xを出力する` | `print()` 関数呼び出し |
| `print(x, y, sep=",")` | `x, yをコンマ区切りで出力する` | `sep` キーワード引数 |
| `len(arr)` | `arrの要素数` | `len()` 関数呼び出し |
| `n ** 2` | `nの2乗` | べき乗で指数が2 |
| `x ** 0.5` | `xの正の平方根` | べき乗で指数が0.5 |
| `int(n ** 0.5)` | `nの正の平方根の整数部分` | `int()` で `** 0.5` をラップ |
| `x is None` | `x ＝ 未定義` | `is None` 比較 |
| `x is not None` | `x ≠ 未定義` | `is not None` 比較 |
| `mat.rows` | `matの行数` | `.rows` 属性アクセス |
| `mat.cols` | `matの列数` | `.cols` 属性アクセス |
| `True` / `False` | `true` / `false` | 定数 |
| `None` | `未定義` | 定数 |

### range() の解析

`for i in range(...)` のパターンを擬似言語の for ループに変換するため、`range()` の引数を詳細に解析する。

```python
# range(start, end + 1) → i を start から end まで 1 ずつ増やす
# range(start, end + 1, step) → i を start から end まで step ずつ増やす
# range(start, end - 1, -1) → i を start から end まで 1 ずつ減らす
# range(start, end - 1, -step) → i を start から end まで step ずつ減らす
```

`_simplify_range_bound()` メソッドで `end + 1` → `end`、`end - 1` → `end` の簡略化を行う。

### 安全名の復元

Phase 1 の擬似言語 → Python 変換で Python 予約語と衝突する識別子に `_` を付加している（例: `in` → `in_`）。逆変換ではこれを検出して元に戻す。

```python
_PYTHON_KEYWORDS = {"in_", "is_", "not_", "and_", "or_", "if_", "for_", "while_", ...}

def _restore_safe_name(self, name: str) -> str:
    if name in self._PYTHON_KEYWORDS:
        return name[:-1]  # 末尾の _ を除去
    return name
```

### import 文のスキップ

Python コードの `import` / `from ... import ...` 文は擬似言語に対応がないため、スキップする。

---

## 作成したファイル

| ファイル | 行数 | 内容 |
|---------|------|------|
| `src/ipa_pseudocode/translator/python_to_pseudo.py` | 約400行 | Python → 擬似言語 逆変換器 |
| `tests/test_reverse_translate.py` | 約430行 | 逆変換テスト 46件 |

## 変更したファイル

| ファイル | 変更内容 |
|---------|---------|
| `src/ipa_pseudocode/__init__.py` | `reverse_translate()` を追加。バージョンを `0.3.0` に |
| `tests/test_integration.py` | バージョンテストを `0.3.0` に更新 |
| `README.md` | 逆変換の使い方・API仕様を追加 |
| `CLAUDE.md` | フェーズ表を更新（Phase 3 完了） |

---

## テスト結果

全 **289テスト** 通過（既存243件 + 新規46件）。

```
tests/test_reverse_translate.py  46 passed
tests/test_executor.py           55 passed
tests/test_trace.py               7 passed
tests/test_integration.py        (既存テストすべて通過)
tests/test_array.py              (既存テストすべて通過)
tests/test_lexer.py              (既存テストすべて通過)
tests/test_parser.py             (既存テストすべて通過)
tests/test_translator.py         (既存テストすべて通過)
tests/test_types.py              (既存テストすべて通過)
```

### テストカテゴリ

| カテゴリ | テスト数 | 内容 |
|---------|---------|------|
| `TestBasicStatements` | 4件 | 代入、型付き代入、None→未定義、bool リテラル |
| `TestArithmeticOperators` | 10件 | 四則演算、整数除算、剰余、比較演算子 |
| `TestControlFlow` | 10件 | if/elif/while/do-while/for/for-each/break/return |
| `TestFunctionDef` | 3件 | 関数定義（型なし/型あり/戻り値なし） |
| `TestSpecialPatterns` | 13件 | swap, append, +=/-=, print, len, 2乗, 平方根, is None, rows/cols, safe name |
| `TestRoundTrip` | 5件 | 擬似言語→Python→擬似言語 の往復変換（意味的等価性を含む） |
| `TestImportSkip` | 1件 | import 文のスキップ |

### 往復変換テスト（Round-Trip）

擬似言語 → Python → 擬似言語 → 実行 の完全な往復テストで **意味的等価性** を検証:

```python
def test_semantic_equivalence(self):
    """往復変換後の擬似言語を実行して、結果が同じであることを確認"""
    pseudo_source = """\
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
"""
    original_result = ipa_pseudocode.call_function(pseudo_source, "total", 10)
    python_code = ipa_pseudocode.translate(pseudo_source)
    reversed_pseudo = ipa_pseudocode.reverse_translate(python_code)
    roundtrip_result = ipa_pseudocode.call_function(reversed_pseudo, "total", 10)

    assert original_result == roundtrip_result == 55
```

---

## 公開 API

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

---

## 実装中に発生した問題と解決

### 1. endif が elseif チェーンで出力されない

**原因:** `_translate_if()` で `elif` を再帰処理した後に早期 `return` していたため、最外の `if` の `endif` が出力されなかった。

**修正:** 再帰後の早期 `return` を削除し、最外の `if` で常に `endif` を出力するようにした。

### 2. swap パターンの検出失敗

**原因:** `_is_swap()` で `ast.dump()` を使って代入先と値の要素を比較していたが、`ctx`（Store/Load）の違いで不一致になった。

**修正:** `self._expr()` で文字列表現に変換してから比較する方式に変更。

### 3. 関数引数の safe name が復元されない

**原因:** 関数パラメータ名（例: `in_`）に `_restore_safe_name()` を適用していなかった。

**修正:** `_translate_function_def()` 内で引数名にも復元処理を追加。

---

## フェーズ進捗

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 1 | core + lexer/parser + 擬似言語→Python変換 | 完了 |
| Phase 2 | executor（擬似言語の直接実行）+ trace | 完了 |
| Phase 3 | Python→擬似言語の逆変換 | **完了** |
| Phase 4 | docs整備 + PyPI公開 + exam-questions充実 | 未着手 |
