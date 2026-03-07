# CLAUDE.md - ipa-pseudocode-toolkit

## プロジェクト概要

情報処理技術者試験（ITパスポート試験・基本情報技術者試験・応用情報技術者試験）の擬似言語を解析・変換・実行・トレースするPythonツールキット。

### 目的

1. IPA擬似言語のパース（字句解析・構文解析）
2. 擬似言語 → Python の変換
3. Python → 擬似言語 の逆変換
4. 擬似言語の直接実行とトレース表生成
5. 公開問題の擬似言語コードのPython変換集を同梱

### 公開形態

- GitHubでPublicリポジトリとして公開
- ライセンス: MIT
- 言語: ドキュメントは日本語メイン、コード中のdocstring・コメントも日本語可
- 変数名・関数名・クラス名は英語

---

## ディレクトリ構成

```
ipa-pseudocode-toolkit/
├── CLAUDE.md                    # 本ファイル
├── README.md
├── LICENSE                      # MIT
├── pyproject.toml               # パッケージ定義
│
├── docs/
│   ├── grammar_spec.md          # 擬似言語の文法仕様（BNF/PEG）
│   ├── mapping_rules.md         # 擬似言語⇔Python対応規則
│   └── examples/                # 変換例集
│
├── src/
│   └── ipa_pseudocode/          # メインパッケージ
│       ├── __init__.py
│       │
│       ├── core/                # 中核データ構造
│       │   ├── __init__.py
│       │   ├── array.py         # 1-based配列クラス
│       │   ├── string.py        # 擬似言語の文字列操作
│       │   └── types.py         # 型定義（整数型、実数型、論理型等）
│       │
│       ├── parser/              # 擬似言語→AST
│       │   ├── __init__.py
│       │   ├── lexer.py         # 字句解析（トークナイザ）
│       │   ├── tokens.py        # トークン定義
│       │   ├── grammar.py       # 構文解析
│       │   └── ast_nodes.py     # ASTノード定義
│       │
│       ├── translator/          # AST⇔コード変換
│       │   ├── __init__.py
│       │   ├── pseudo_to_python.py   # 擬似言語→Python
│       │   ├── python_to_pseudo.py   # Python→擬似言語
│       │   └── codegen.py            # コード生成共通処理
│       │
│       ├── runtime/             # 実行環境
│       │   ├── __init__.py
│       │   ├── executor.py      # 擬似言語コード実行エンジン
│       │   ├── builtins.py      # 組込み関数（表示、改行など）
│       │   └── trace.py         # トレース表（実行過程の記録）
│       │
│       └── utils/               # ユーティリティ
│           ├── __init__.py
│           ├── formatter.py     # 擬似言語の整形出力
│           └── validator.py     # 構文検証
│
├── tests/
│   ├── conftest.py
│   ├── test_array.py
│   ├── test_parser.py
│   ├── test_translator.py
│   ├── test_executor.py
│   └── fixtures/                # テスト用擬似言語コード
│       ├── ipa_samples/
│       └── edge_cases/
│
├── exam-questions/              # 公開問題の擬似言語→Python変換集
│   ├── README.md                # 出典・ライセンス表記（IPA公開問題の利用条件）
│   ├── ip/                      # ITパスポート試験
│   │   └── {年度-期}/
│   │       ├── q{番号}.pseudo
│   │       └── q{番号}.py
│   ├── fe/                      # 基本情報技術者試験
│   │   └── {年度-期}/
│   │       ├── q{番号}.pseudo
│   │       └── q{番号}.py
│   └── ap/                      # 応用情報技術者試験
│       └── {年度-期}/
│           ├── q{番号}.pseudo
│           └── q{番号}.py
│
└── examples/
    ├── basic_usage.py
    ├── translate_demo.py
    └── trace_demo.py
```

---

## 擬似言語の仕様

### 参照元

IPAが公開している擬似言語の仕様書（Ver.5.1、2024年4月試験から適用）:
https://www.ipa.go.jp/shiken/syllabus/doe3um0000002djj-att/shiken_yougo_ver5_1.pdf

- 別紙1: ITパスポート試験用
- 別紙2: 基本情報技術者試験，応用情報技術者試験用（Ver.5.1でAP追加）

### 主要な特徴（Python との相違点）

| 擬似言語 | Python |
|----------|--------|
| 配列の添字は **1始まり** | 0始まり |
| `整数型: x` のような型宣言あり | 型宣言不要 |
| `if (条件式) ... elseif ... else ... endif` | `if ... : elif ... : else:` |
| `while (条件式) ... endwhile` | `while ... :` |
| `do ... while (条件式)` | （対応構文なし） |
| `for (制御記述) ... endfor` | `for ... :` |
| `○手続名又は関数名` | `def` |
| `変数名 ← 式` | `変数名 = 式` |
| `未定義` / `未定義の値` | `None` |
| 論理演算: `and`, `or`, `not` | `and`, `or`, `not` |
| 乗除: `×`, `÷`, `÷...の商`, `mod` | `*`, `/`, `//`, `%` |
| 減算: `−`(U+2212), `－`(U+FF0D), `ー`(U+30FC) | `-` |
| 関係: `＝`, `≠`, `＜`, `＞`, `≦`, `≧` | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| メンバアクセス: `.`（FE/AP用） | `.` |
| 文字列結合: `+` | `+` |
| `true`, `false` | `True`, `False` |

### 1-based配列の設計方針

擬似言語の配列は添字が1から始まる。これをPythonで表現するために専用クラスを用意する。

```python
class Array:
    """IPA擬似言語の1-based配列"""

    def __init__(self, size, init=None):
        """
        Args:
            size: 配列の要素数
            init: 初期値（デフォルトはNone=未定義）
        """
        self._data = [init] * size
        self._size = size

    def __getitem__(self, index):
        if not (1 <= index <= self._size):
            raise IndexError(f"添字が範囲外です: {index}（有効範囲: 1〜{self._size}）")
        return self._data[index - 1]

    def __setitem__(self, index, value):
        if not (1 <= index <= self._size):
            raise IndexError(f"添字が範囲外です: {index}（有効範囲: 1〜{self._size}）")
        self._data[index - 1] = value

    def __len__(self):
        return self._size

    def __repr__(self):
        return f"Array({self._data})"
```

二次元配列: `Array2D` クラスとして別途定義する。

---

## 変換パイプライン

```
擬似言語テキスト
    ↓  lexer.py（字句解析）
トークン列
    ↓  grammar.py（構文解析）
AST（抽象構文木）
    ↓  pseudo_to_python.py / python_to_pseudo.py
Python / 擬似言語テキスト
```

- 擬似言語→Python: lexer→parser→AST→Pythonコード生成
- Python→擬似言語: Python標準ライブラリの `ast` モジュールでパース→独自AST→擬似言語コード生成
- 擬似言語実行: lexer→parser→AST→executor（ASTを直接走査して実行）

---

## 開発方針

### フェーズ分け

| フェーズ | 内容 | 状態 |
|---------|------|------|
| Phase 1 | core（Array等）+ lexer/parser + 擬似言語→Python変換 | 完了 |
| Phase 2 | executor（擬似言語の直接実行）+ trace | 完了 |
| Phase 3 | Python→擬似言語の逆変換 | ← 今ここ |
| Phase 4 | docs整備 + PyPI公開 + exam-questions充実 | 未着手 |

### コーディング規約

- Python 3.10以上を対象
- 型ヒント（type hints）を積極的に使用
- docstringは日本語でも可（公開APIは日英併記が望ましい）
- フォーマッタ: ruff
- リンタ: ruff
- テスト: pytest
- エラーメッセージは日本語（教育用途のため学習者にわかりやすく）

### テスト方針

- 各モジュールに対応するテストファイルを `tests/` に配置
- テスト用の擬似言語コードは `tests/fixtures/` に `.pseudo` ファイルとして保存
- IPA公開問題からの変換結果を回帰テストに活用

### コミットメッセージ

日本語でも英語でもよいが、プレフィックスを付ける:
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント
- `test:` テスト追加・修正
- `refactor:` リファクタリング
- `chore:` 設定・雑務
