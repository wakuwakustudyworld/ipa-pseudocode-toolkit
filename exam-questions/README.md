# exam-questions — IPA公開問題の擬似言語・Python変換集

## 出典・ライセンス

本ディレクトリに収録している擬似言語コード（`.pseudo`ファイル）は、独立行政法人 情報処理推進機構（IPA）が公開している情報処理技術者試験の問題を基に作成したものです。

### 出典

#### ITパスポート試験

問題PDFは [ITパスポート試験 CBT疑似体験ソフトウェア・公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/questions.html) よりダウンロード可能。

- **サンプル問題**: [ITパスポート試験 擬似言語サンプル問題](https://www.ipa.go.jp/shiken/syllabus/ps6vr7000000i9in-att/ip_programming_sample.pdf)
- **令和4年度公開問題**: [令和4年度 ITパスポート試験 公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/pdf/questions/2022r04_ip_qs.pdf)
- **令和5年度公開問題**: [令和5年度 ITパスポート試験 公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/pdf/questions/2023r05_ip_qs.pdf)
- **令和6年度公開問題**: [令和6年度 ITパスポート試験 公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/pdf/questions/2024r06_ip_qs.pdf)
- **令和7年度公開問題**: [令和7年度 ITパスポート試験 公開問題](https://www3.jitec.ipa.go.jp/JitesCbt/html/openinfo/pdf/questions/2025r07_ip_qs.pdf)

#### 基本情報技術者試験

問題PDFは [基本情報技術者試験 公開問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/sg_fe/koukai/index.html) よりダウンロード可能。

- **サンプル問題**: [基本情報技術者試験 科目B試験 サンプル問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/ps6vr70000010d6y-att/fe_kamoku_b_sample.pdf)
- **サンプル問題セット**: [基本情報技術者試験 科目B サンプル問題セット](https://www.ipa.go.jp/shiken/mondai-kaiotu/ps6vr70000010d6y-att/fe_kamoku_b_set_sample.pdf)
- **令和5年度公開問題**: [令和5年度 基本情報技術者試験 科目B 公開問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/ps6vr70000010d6y-att/fe_kamoku_b_kokai_2023r05.pdf)
- **令和6年度公開問題**: [令和6年度 基本情報技術者試験 科目B 公開問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/gmcbt80000007np7-att/fe_kamoku_b_kokai_2024r06.pdf)
- **令和7年度公開問題**: [令和7年度 基本情報技術者試験 科目B 公開問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/gmcbt80000007np7-att/fe_kamoku_b_kokai_2025r07.pdf)

#### 応用情報技術者試験

問題PDFは [IPA 情報処理技術者試験 過去問題](https://www.ipa.go.jp/shiken/mondai-kaiotu/index.html) よりダウンロード可能。

- **令和6年春 午後**: [令和6年春 応用情報技術者試験 午後](https://www.ipa.go.jp/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06h_ap_pm_qs.pdf) 問3
- **令和6年秋 午後**: [令和6年秋 応用情報技術者試験 午後](https://www.ipa.go.jp/shiken/mondai-kaiotu/m42obm000000afqx-att/2024r06a_ap_pm_qs.pdf) 問3
- **令和7年春 午後**: [令和7年春 応用情報技術者試験 午後](https://www.ipa.go.jp/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07h_ap_pm_qs.pdf) 問3
- **令和7年秋 午後**: [令和7年秋 応用情報技術者試験 午後](https://www.ipa.go.jp/shiken/mondai-kaiotu/nl10bi0000009lh8-att/2025r07a_ap_pm_qs.pdf) 問3

### IPA公開問題の利用について

IPA公開問題は、試験の準備に資するために公開されているものです。本リポジトリでは、問題中の擬似言語コード部分のみを抜粋して `.pseudo` 形式で収録し、それを本ツールキットでPythonに変換した `.py` ファイルを同梱しています。問題文そのものは収録していません。

### ライセンス

本ディレクトリ内のファイルについて:
- **`.pseudo`ファイル**: IPA公開問題の擬似言語コード部分に基づく（IPAの利用条件に従う）
- **`.py`ファイル**: 本ツールキット（`ipa_pseudocode`）による機械的な変換結果（一部手動修正あり）。変換コード自体はMITライセンス

---

## 収録内容

### ITパスポート試験（ip/）

| ディレクトリ | 試験 | 問題数 | 備考 |
|-------------|------|--------|------|
| `ip/sample/` | 擬似言語サンプル問題 | 問1〜問2（2問） | |
| `ip/2022r04/` | 令和4年度 公開問題 | 問78, 問96（2問） | |
| `ip/2023r05/` | 令和5年度 公開問題 | 問60, 問64（2問） | |
| `ip/2024r06/` | 令和6年度 公開問題 | 問62, 問85（2問） | |
| `ip/2025r07/` | 令和7年度 公開問題 | 問78, 問99（2問） | |

IP合計: 10問

### 基本情報技術者試験（fe/）

| ディレクトリ | 試験 | 問題数 | 備考 |
|-------------|------|--------|------|
| `fe/sample/` | 科目B サンプル問題 | 問1〜問5（5問） | |
| `fe/set-sample/` | 科目B サンプル問題セット | 問1〜問16（15問） | 問15は擬似言語なし |
| `fe/2023r05/` | 令和5年度 科目B 公開問題 | 問1〜問5（5問） | |
| `fe/2024r06/` | 令和6年度 科目B 公開問題 | 問1〜問5（5問） | |
| `fe/2025r07/` | 令和7年度 科目B 公開問題 | 問1〜問5（5問） | |

FE合計: 35問

### 応用情報技術者試験（ap/）

| ディレクトリ | 試験 | 問題数 | 概要 |
|-------------|------|--------|------|
| `ap/2024r06h/` | 令和6年春 午後 問3 | 1問 | ダイクストラ法による最短距離・最短経路 |
| `ap/2024r06a/` | 令和6年秋 午後 問3 | 1問 | エラトステネスの篩による素数列挙（3段階の改良） |
| `ap/2025r07h/` | 令和7年春 午後 問3 | 1問 | スライドパズルの最小解を幅優先探索で求める |
| `ap/2025r07a/` | 令和7年秋 午後 問3 | 1問 | 動的計画法による最長共通部分列（LCS）の長さ |

AP合計: 4問

**全体合計: 49問**（`.pseudo` + `.py` 各49）

---

## ファイル形式

- **`.pseudo`**: IPA擬似言語のソースコード。先頭のコメント行に出典と正解を記載
- **`.py`**: `ipa_pseudocode.translate()` による自動変換結果。手動修正を加えた箇所には `# 手動変換:` コメントを付記

---

## 変換結果

全49ファイルが `ipa_pseudocode.translate()` による自動変換でPythonとして構文的に有効なコードに変換される（`py_compile` 通過）。

### ITパスポート試験

#### 完全自動変換（10ファイル / 10問中）

- `ip/sample/`: q01, q02
- `ip/2022r04/`: q78, q96
- `ip/2023r05/`: q60, q64
- `ip/2024r06/`: q62, q85
- `ip/2025r07/`: q78, q99

### 基本情報技術者試験

#### 完全自動変換（35ファイル / 35問中）

- `fe/sample/`: q01〜q05
- `fe/set-sample/`: q01〜q14, q16（全15ファイル）
- `fe/2023r05/`: q01〜q05
- `fe/2024r06/`: q01〜q05
- `fe/2025r07/`: q01〜q05

### 応用情報技術者試験

#### 完全自動変換（4ファイル / 4問中）

| ファイル | 概要 | 備考 |
|---------|------|------|
| `ap/2024r06h/q03.pseudo` | ダイクストラ法 | 複合条件（`かつ`）、外部変数、二次元配列 |
| `ap/2024r06a/q03.pseudo` | エラトステネスの篩 | 3関数の段階的改良、整数除算（`÷...の商`）のインデックス計算 |
| `ap/2025r07h/q03.pseudo` | スライドパズル（BFS） | クラス型変数、メソッド呼び出し、`かつ`条件 |
| `ap/2025r07a/q03.pseudo` | 最長共通部分列（LCS） | 二次元配列の動的初期化（カンマ形式） |

AP問題の自動変換出力は外部クラス（`BoardState`, `Queue`, `List`）や未定義の関数（`createGoal`, `checkGoal` 等）を参照するため、単独では実行できない。同梱の `.py` ファイルは手動で補完したスタンドアロン実行可能版である。

---

## 注意事項

- `.py`ファイルはPythonとして構文的に有効（`py_compile`通過）
- 擬似言語の配列（添字1始まり）は `ipa_pseudocode.core.array.Array` / `Array2D` クラスを使って変換されるため、1-basedの添字アクセスがそのまま正しく動作する
- AP問題の `.py` ファイルは手動変換によるスタンドアロン実行可能版（標準Pythonのリストや独自クラスを使用）
- `.py` ファイルの実行には `ipa_pseudocode` パッケージのインストールが必要（`pip install -e .`）
- 問題の空欄（正解）は `.pseudo` ファイル作成時に埋めてある。正解は各 `.pseudo` ファイル先頭のコメントに記載
