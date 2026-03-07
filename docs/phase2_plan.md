# Phase 2 実装計画: Executor & Trace

## 概要

Phase 1 で構築した Lexer → Parser → AST パイプラインを活用し、擬似言語を **Python に変換せずに直接実行** するエンジン（Executor）と、実行過程を記録する **トレース表** 機能（Trace）を実装する。

### 目的

1. **教育用途**: 擬似言語コードをステップ実行し、各ステップでの変数の変化を可視化する
2. **検証用途**: Python 変換結果と直接実行結果を突き合わせて、変換の正しさを検証する
3. **試験対策**: IPA 試験のトレース問題（変数の値を追跡する問題）の自動解答・解説生成

---

## 実装対象モジュール

```
src/ipa_pseudocode/runtime/
├── __init__.py
├── executor.py      # AST直接実行エンジン
├── builtins.py      # 組込み関数・操作
└── trace.py         # トレース表（実行過程の記録・出力）
```

---

## Step 1: `runtime/executor.py` — 実行エンジン

### 1.1 アーキテクチャ

AST を Visitor パターンで走査し、各ノードを評価・実行する。

```python
class Executor:
    def __init__(self, trace_enabled: bool = False):
        self._global_scope: dict[str, Any]       # グローバル変数
        self._call_stack: list[dict[str, Any]]    # 関数呼び出しスタック
        self._functions: dict[str, FunctionDef]   # ユーザー定義関数テーブル
        self._tracer: Tracer | None               # トレース記録（オプション）
        self._output: list[str]                   # 出力バッファ

    def execute(self, program: Program) -> ExecutionResult:
        """プログラム全体を実行する"""

    # --- 文の実行 ---
    def _exec_stmt(self, stmt: Statement) -> None
    def _exec_var_decl(self, stmt: VarDecl) -> None
    def _exec_assignment(self, stmt: Assignment) -> None
    def _exec_if(self, stmt: IfStatement) -> None
    def _exec_while(self, stmt: WhileStatement) -> None
    def _exec_do_while(self, stmt: DoWhileStatement) -> None
    def _exec_for(self, stmt: ForStatement) -> None
    def _exec_for_each(self, stmt: ForEachStatement) -> None
    def _exec_return(self, stmt: ReturnStatement) -> None
    def _exec_break(self, stmt: BreakStatement) -> None
    def _exec_print(self, stmt: PrintStatement) -> None
    def _exec_swap(self, stmt: SwapStatement) -> None
    def _exec_append(self, stmt: AppendStatement) -> None
    def _exec_increment(self, stmt: IncrementStatement) -> None

    # --- 式の評価 ---
    def _eval_expr(self, expr: Expression) -> Any
    def _eval_binary_op(self, expr: BinaryOp) -> Any
    def _eval_unary_op(self, expr: UnaryOp) -> Any
    def _eval_function_call(self, expr: FunctionCall) -> Any
    def _eval_array_access(self, expr: ArrayAccess) -> Any
    def _eval_member_access(self, expr: MemberAccess) -> Any
    def _eval_property_access(self, expr: PropertyAccess) -> Any
    def _eval_char_at(self, expr: CharAt) -> str
    def _eval_dynamic_array_init(self, expr: DynamicArrayInit) -> Array | Array2D
```

### 1.2 スコープ管理

```
┌──────────────────────────────┐
│  グローバルスコープ            │  Program.globals の VarDecl
│  _global_scope               │
├──────────────────────────────┤
│  関数スコープ (スタック)       │  関数呼び出しごとにpush/pop
│  _call_stack[-1]             │  仮引数 + ローカル変数
└──────────────────────────────┘
```

**変数解決の優先順位:**
1. ローカルスコープ（`_call_stack[-1]`）
2. グローバルスコープ（`_global_scope`）

**グローバル変数への代入:**
- `VarDecl.is_global == True` の変数はグローバルスコープに格納
- 関数内でグローバル変数に代入する場合、グローバルスコープを直接更新

### 1.3 制御フロー

制御フローの中断（`return`, `break`）は例外ベースで実装する:

```python
class _ReturnSignal(Exception):
    def __init__(self, value: Any = None):
        self.value = value

class _BreakSignal(Exception):
    def __init__(self, label: str | None = None):
        self.label = label
```

- `return` → `_ReturnSignal` を raise、関数呼び出し側で catch
- `break` → `_BreakSignal` を raise、対応するループで catch
- ラベル付き break → `_BreakSignal(label="α")` でラベルを伝搬

### 1.4 演算子の評価

| AST の op | 実行時の処理 |
|-----------|-------------|
| `+` | 数値加算 or 文字列結合（型で判定） |
| `−` | 減算 |
| `×` | 乗算 |
| `÷` | 実数除算（`/`） |
| `÷...の商` / `整数除算` | 整数除算（`//`） |
| `÷...の余り` / `mod` | 剰余（`%`） |
| `＝` | 等値比較（`==`） |
| `≠` | 非等値（`!=`） |
| `＜`, `＞`, `≦`, `≧` | 比較演算 |
| `and`, `or` | 短絡評価（左辺が確定したら右辺を評価しない） |
| `not` | 論理否定 |
| `**` | べき乗 |

### 1.5 関数呼び出し

```
1. 引数を評価（左から右）
2. 新しいローカルスコープを作成
3. 仮引数に実引数をバインド
4. 関数本体を実行
5. _ReturnSignal を catch して戻り値を取得
6. スコープをpop
```

**注意:** 配列引数が値渡しか参照渡しかは、IPA仕様上は明示されていない。実際の試験問題の挙動から、**配列は参照渡し**（Python のデフォルトと同じ）として扱う。

### 1.6 実行結果

```python
@dataclass
class ExecutionResult:
    output: list[str]          # 出力された文字列のリスト
    return_value: Any          # トップレベルの戻り値（あれば）
    trace: TraceTable | None   # トレース表（有効時のみ）
    global_vars: dict[str, Any]  # 実行後のグローバル変数状態
```

---

## Step 2: `runtime/builtins.py` — 組込み関数・操作

### 2.1 対応する組込み関数

Phase 1 の変換ロジックと試験問題から抽出した、executor が処理すべき組込み操作:

| 擬似言語の表現 | AST ノード | executor での処理 |
|---------------|-----------|------------------|
| `○○を出力する` | `PrintStatement` | 出力バッファに追加 |
| `○○の要素数` | `PropertyAccess("要素数")` | `len(obj)` |
| `○○の文字数` | `PropertyAccess("文字数")` | `len(obj)` |
| `○○の行数` | `PropertyAccess("行数")` | `obj.rows` |
| `○○の列数` | `PropertyAccess("列数")` | `obj.cols` |
| `○○のi文字目の文字` | `CharAt` | `obj[index - 1]`（文字列は0-based） |
| `○○の2乗` | `BinaryOp("**", expr, 2)` | `expr ** 2` |
| `○○の正の平方根` | `BinaryOp("**", expr, 0.5)` | `expr ** 0.5` |
| `○○の正の平方根の整数部分` | `FunctionCall(int, sqrt)` | `int(expr ** 0.5)` |
| `{n個のx}` | `DynamicArrayInit` | `Array(n, init=x)` |
| `{r行c列のx}` | `DynamicArrayInit` | `Array2D(r, c, init=x)` |

### 2.2 組込み関数レジストリ

```python
class BuiltinRegistry:
    """組込み関数のレジストリ"""

    def __init__(self):
        self._functions: dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self):
        # 将来の拡張用（ユーザー定義の組込み関数追加に対応）
        pass

    def is_builtin(self, name: str) -> bool: ...
    def call(self, name: str, args: list[Any]) -> Any: ...
```

**注:** 現時点では IPA 擬似言語に明示的な組込み関数は少ない（大部分は日本語アクション文として AST ノードになっている）。レジストリは将来の拡張性のために用意するが、初期実装はシンプルに保つ。

---

## Step 3: `runtime/trace.py` — トレース表

### 3.1 目的

IPA 試験のトレース問題では「プログラム実行後の変数の値」や「ループの各反復での変数値」を問う。Tracer はこれを自動生成する。

### 3.2 データモデル

```python
@dataclass
class TraceStep:
    step_number: int              # ステップ番号（1始まり）
    line_description: str         # 実行した文の説明（例: "x ← y + 1"）
    node_type: str                # ASTノードの種別
    variables: dict[str, Any]     # このステップ時点の全変数のスナップショット
    scope: str                    # "global" or 関数名
    event: str                    # "assign" | "call" | "return" | "branch" | "loop_start" | "loop_end" | "output"
    detail: str                   # 補足情報（例: "条件: true → then分岐"）

@dataclass
class TraceTable:
    steps: list[TraceStep]
    columns: list[str]            # トレース対象の変数名リスト

    def to_markdown(self) -> str: ...
    def to_csv(self) -> str: ...
    def to_dict(self) -> list[dict]: ...
```

### 3.3 記録タイミング

以下のイベント発生時に TraceStep を記録する:

| イベント | 記録内容 |
|---------|---------|
| 変数宣言 (`VarDecl`) | 変数名と初期値 |
| 代入 (`Assignment`) | 代入先と新しい値 |
| 条件分岐 (`IfStatement`) | 条件式の評価結果、どの分岐に入ったか |
| ループ開始 (`For/While`) | ループ変数の初期値 |
| ループ反復 | ループ変数の更新値 |
| ループ終了 | 終了条件 |
| 関数呼び出し (`FunctionCall`) | 関数名、実引数 |
| 関数復帰 (`Return`) | 戻り値 |
| 出力 (`PrintStatement`) | 出力内容 |
| swap / append / increment | 操作前後の値 |

### 3.4 出力形式

**Markdown テーブル例:**

```markdown
| Step | 文 | x | y | z | 出力 |
|------|-----|---|---|---|------|
| 1 | x ← 1 | 1 | - | - | |
| 2 | y ← 2 | 1 | 2 | - | |
| 3 | z ← 3 | 1 | 2 | 3 | |
| 4 | x ← y | 2 | 2 | 3 | |
| 5 | y ← z | 2 | 3 | 3 | |
| 6 | z ← x | 2 | 3 | 2 | |
| 7 | 出力 | 2 | 3 | 2 | 3, 2 |
```

### 3.5 Tracer クラス

```python
class Tracer:
    """Executor に組み込まれるトレース記録コンポーネント"""

    def __init__(self):
        self._steps: list[TraceStep] = []
        self._step_counter: int = 0
        self._watched_vars: set[str] | None = None  # None=全変数を記録

    def record(self, description: str, variables: dict, scope: str,
               event: str, detail: str = "") -> None:
        """1ステップを記録する"""

    def set_watch(self, var_names: list[str]) -> None:
        """特定の変数のみを記録対象にする（トレース表の列を絞る）"""

    def build_table(self) -> TraceTable:
        """記録したステップからTraceTableを構築する"""
```

---

## Step 4: 公開 API の拡張

### 4.1 `__init__.py` に追加する関数

```python
def execute(source: str, **kwargs) -> ExecutionResult:
    """擬似言語ソースコードを直接実行する

    Args:
        source: 擬似言語ソースコード
        **kwargs: 関数呼び出し用の引数（トップレベル関数の実行時）

    Returns:
        ExecutionResult（出力、戻り値、トレース表など）
    """

def trace(source: str, watch: list[str] | None = None) -> TraceTable:
    """擬似言語ソースコードを実行し、トレース表を返す

    Args:
        source: 擬似言語ソースコード
        watch: トレース対象の変数名リスト（Noneで全変数）

    Returns:
        TraceTable
    """
```

### 4.2 関数を指定して実行するAPI

試験問題では「関数を定義して、特定の引数で呼び出す」パターンが多い:

```python
def call_function(source: str, func_name: str, *args) -> Any:
    """擬似言語で定義された関数を指定引数で呼び出す

    Args:
        source: 擬似言語ソースコード（関数定義を含む）
        func_name: 呼び出す関数名
        *args: 関数に渡す引数

    Returns:
        関数の戻り値
    """
```

---

## Step 5: テスト計画

### 5.1 テストファイル構成

```
tests/
├── test_executor.py          # executor 単体テスト
├── test_trace.py             # トレース表テスト
└── test_executor_exam.py     # 試験問題を使った統合テスト（オプション）
```

### 5.2 `test_executor.py` のテストケース

既存の `test_integration.py` のテストパターンを executor 版に移植する。exec() を使わず、executor で直接実行する。

**基本機能テスト:**

| テスト | 検証内容 |
|--------|---------|
| `test_var_decl_and_assign` | 変数宣言・代入・参照 |
| `test_arithmetic` | 四則演算（`+`, `−`, `×`, `÷`） |
| `test_integer_division` | 整数除算（`÷...の商`） |
| `test_mod` | 剰余（`mod`, `÷...の余り`） |
| `test_comparison` | 比較演算子（`＝`, `≠`, `＜`, `＞`, `≦`, `≧`） |
| `test_boolean_logic` | 論理演算（`and`, `or`, `not`） |
| `test_if_elseif_else` | 条件分岐 |
| `test_while_loop` | while ループ |
| `test_do_while_loop` | do-while ループ |
| `test_for_increment` | for（増加） |
| `test_for_decrement` | for（減少） |
| `test_for_each` | for-each |
| `test_nested_loops` | ネストしたループ |
| `test_break` | break |
| `test_labeled_break` | ラベル付き break |
| `test_function_call` | 関数呼び出し・戻り値 |
| `test_recursion` | 再帰関数 |
| `test_global_variable` | グローバル変数の読み書き |
| `test_array_1based` | 1-based 配列アクセス |
| `test_array_2d` | 二次元配列 |
| `test_dynamic_array` | 動的配列初期化 `{n個のx}` |
| `test_append` | 末尾追加 |
| `test_swap` | 値の入れ替え |
| `test_increment_decrement` | 値の増減 |
| `test_print_output` | 出力 |
| `test_print_separator` | 区切り付き出力 |
| `test_property_access` | 要素数・文字数 |
| `test_char_at` | 文字アクセス |
| `test_math_patterns` | 2乗・平方根 |
| `test_undefined_value` | 未定義値 |

### 5.3 `test_trace.py` のテストケース

| テスト | 検証内容 |
|--------|---------|
| `test_simple_trace` | 代入のトレース（変数値のスナップショット） |
| `test_loop_trace` | ループのトレース（反復ごとの変数値） |
| `test_branch_trace` | 条件分岐のトレース（どの分岐に入ったか） |
| `test_function_call_trace` | 関数呼び出しのトレース（スコープ変化） |
| `test_trace_watch` | 特定変数のみのトレース |
| `test_trace_to_markdown` | Markdown テーブル出力 |
| `test_trace_to_csv` | CSV 出力 |
| `test_exam_q01_trace` | set-sample/q01（変数の入れ替え）のトレース検証 |

### 5.4 試験問題による統合テスト

`exam-questions/fe/` の `.pseudo` ファイルを executor で直接実行し、対応する `.py` ファイルの exec() 結果と一致することを検証する。

---

## 実装順序とマイルストーン

### Milestone 1: 最小限の Executor（式評価＋基本文）

**対象:**
- リテラル評価（整数、実数、文字列、論理値、未定義）
- 変数宣言・代入・参照
- 四則演算・比較・論理演算
- if / elseif / else
- while / do-while
- print（基本出力）

**検証:** 簡単な擬似言語コード（変数操作 + 条件分岐 + ループ）が実行できること

### Milestone 2: 関数・配列・制御フロー

**対象:**
- 関数定義・呼び出し・return
- 再帰
- for ループ（increment / decrement / each）
- break（ラベル付き含む）
- 配列（Array / Array2D）アクセス
- グローバル変数

**検証:** `test_integration.py` の全テストケースを executor で再現

### Milestone 3: 日本語アクション文・プロパティ

**対象:**
- swap / append / increment
- PropertyAccess（要素数、文字数、行数、列数）
- CharAt
- DynamicArrayInit
- 数学パターン（2乗、平方根）
- 区切り付き出力

**検証:** 試験問題（exam-questions）の実行

### Milestone 4: トレース表

**対象:**
- Tracer の実装
- Executor へのトレースフック組み込み
- TraceTable の出力（Markdown / CSV）
- 公開 API（`execute()`, `trace()`, `call_function()`）

**検証:** set-sample/q01 のトレース表が期待通りに生成されること

---

## 設計上の判断事項

### Q1: 配列は値渡しか参照渡しか？

**方針:** 参照渡し（Python のデフォルト挙動と同じ）。IPA 仕様では明記されていないが、試験問題の挙動からこちらが自然。必要に応じて深いコピー（`copy.deepcopy`）オプションを用意する。

### Q2: 未宣言変数へのアクセスはエラーか？

**方針:** `RuntimeError` を raise する。擬似言語は型宣言が必須なので、宣言なしの変数参照はプログラムの誤りとして扱う。

### Q3: 型チェックはどこまで行うか？

**方針:** Phase 2 では **動的型付け**（Python と同じ）とする。型宣言は変数の存在を示すために使い、型の不一致は実行時エラー（Python の自然なエラー）に任せる。将来的に静的型チェック機能を追加する余地は残す。

### Q4: 出力の扱い

**方針:** `print()` を直接呼ばず、内部の出力バッファ（`list[str]`）に蓄積する。これにより、テストでの出力検証が容易になり、トレース表にも出力内容を記録できる。

### Q5: 無限ループの検出

**方針:** 最大ステップ数（デフォルト: 100,000）を設定し、超過時に `RuntimeError` を raise する。`execute()` のオプションで変更可能にする。

---

## 実装結果

**実装日:** 2026-03-07
**バージョン:** 0.2.0

### 作成したファイル

| ファイル | 行数 | 内容 |
|---------|------|------|
| `src/ipa_pseudocode/runtime/__init__.py` | 15行 | モジュール公開API |
| `src/ipa_pseudocode/runtime/executor.py` | 約420行 | AST直接実行エンジン（Visitor パターン） |
| `src/ipa_pseudocode/runtime/builtins.py` | 約30行 | 組込み関数レジストリ（`int`, `float`, `str`, `abs`, `len`） |
| `src/ipa_pseudocode/runtime/trace.py` | 約150行 | トレース記録 + TraceTable出力（Markdown/CSV/dict） |
| `tests/test_executor.py` | 約350行 | Executor テスト 55件 |
| `tests/test_trace.py` | 約110行 | トレース表テスト 7件 |

### 変更したファイル

| ファイル | 変更内容 |
|---------|---------|
| `src/ipa_pseudocode/__init__.py` | `execute()`, `call_function()`, `trace()` を追加。バージョンを `0.2.0` に |
| `tests/test_integration.py` | バージョンテストを `0.2.0` に更新 |
| `README.md` | 直接実行・トレース機能の説明とAPI仕様を追加 |
| `CLAUDE.md` | フェーズ表を更新（Phase 2 完了） |

### テスト結果

全 **243テスト** 通過（既存181件 + 新規62件）。

```
tests/test_executor.py   55 passed
tests/test_trace.py       7 passed
tests/test_integration.py (既存テストすべて通過)
tests/test_array.py       (既存テストすべて通過)
tests/test_lexer.py       (既存テストすべて通過)
tests/test_parser.py      (既存テストすべて通過)
tests/test_translator.py  (既存テストすべて通過)
tests/test_types.py       (既存テストすべて通過)
```

### 実装したExecutorの主要機能

**式の評価:**
- リテラル（整数、実数、文字列、論理値、未定義、−∞）
- 二項演算（四則演算、比較、論理演算、ビット演算、べき乗）— 短絡評価対応
- 単項演算（`not`, `+`, `-`）
- 配列アクセス（1-based、1D/2D）
- 関数呼び出し（ユーザー定義 + 組込み）
- プロパティアクセス（要素数、文字数、行数、列数）
- 文字アクセス（CharAt、1-based）
- 動的配列初期化（`{n個のx}`, `{r行c列のx}`）
- 配列リテラル（ネスト配列→Array2D自動変換）

**文の実行:**
- 変数宣言・代入（スコープ管理: グローバル/ローカル）
- 条件分岐（if / elseif / else）
- ループ（while, do-while, for increment/decrement, for-each）
- 関数定義・呼び出し・再帰（コールスタック方式）
- return / break（例外ベースのシグナル伝搬、ラベル付きbreak対応）
- 出力（区切り指定対応、内部バッファに蓄積）
- swap / append / increment

**安全機構:**
- 最大ステップ数（デフォルト100,000）による無限ループ検出
- 未宣言変数アクセス時の `RuntimeError`
- ゼロ除算の検出

### 公開API

```python
import ipa_pseudocode

# 擬似言語を直接実行
result = ipa_pseudocode.execute(source, trace_enabled=False)
# result.output       — 出力文字列のリスト
# result.return_value — トップレベルの戻り値
# result.trace        — TraceTable（trace_enabled=True時）
# result.global_vars  — 実行後のグローバル変数

# 関数を指定して呼び出し
val = ipa_pseudocode.call_function(source, "funcName", arg1, arg2)

# トレース表を生成
table = ipa_pseudocode.trace(source, watch=["x", "y"])
table.to_markdown()  # Markdownテーブル
table.to_csv()       # CSV
table.to_dict()      # 辞書のリスト
```

### 設計判断の実装結果

| 判断事項 | 計画通り実装 | 備考 |
|---------|-------------|------|
| 配列は参照渡し | Yes | Python のデフォルト挙動に従う |
| 未宣言変数でエラー | Yes | `RuntimeError("変数 'x' が定義されていません")` |
| 動的型付け | Yes | 型宣言は変数の存在確認のみ |
| 出力は内部バッファ | Yes | `ExecutionResult.output` で取得 |
| 無限ループ検出 | Yes | `Executor(max_steps=100_000)` で制御 |
| 制御フローは例外ベース | Yes | `_ReturnSignal`, `_BreakSignal` |
