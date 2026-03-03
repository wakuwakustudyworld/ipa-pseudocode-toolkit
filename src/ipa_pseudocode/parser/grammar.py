"""構文解析器（パーサー）

IPA擬似言語のソースコードを解析してASTを生成する。
行ベースの正規表現分類＋再帰下降パーサー＋Prattパーサーのハイブリッド構成。
"""

from __future__ import annotations

import re
from typing import Any

from .ast_nodes import (
    AppendStatement,
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOp,
    BooleanLiteral,
    BreakStatement,
    DoWhileStatement,
    DynamicArrayInit,
    ElseIfClause,
    Expression,
    ExpressionStatement,
    ForEachStatement,
    ForStatement,
    FunctionCall,
    FunctionDef,
    Identifier,
    IfStatement,
    IncrementStatement,
    IntegerLiteral,
    MemberAccess,
    NegativeInfinity,
    Parameter,
    PrintStatement,
    Program,
    PropertyAccess,
    RealLiteral,
    ReturnStatement,
    StringLiteral,
    SwapStatement,
    UnaryOp,
    UndefinedLiteral,
    VarDecl,
    WhileStatement,
)
from .lexer import Lexer
from .tokens import Token, TokenType

# --- 行分類用の正規表現 ---

_FUNC_DEF_RE = re.compile(
    r"^○\s*(?:(.+?)\s*[:：]\s*)?(\w+)\s*\(([^)]*)\)\s*$"
)
_GLOBAL_VAR_RE = re.compile(
    r"^大域\s*[:：]\s*(.+)$"
)
_VAR_DECL_RE = re.compile(
    r"^(.+?型[^:：]*?|[A-Z]\w+)\s*[:：]\s*(.+)$"
)
_ASSIGNMENT_RE = re.compile(
    r"^(.+?)\s*←\s*(.+)$"
)
_FOR_STANDARD_RE = re.compile(
    r"^for\s*\(\s*(\w+)\s*を\s*(.+?)\s*から\s*(.+?)\s*まで\s*(.+?)\s*ずつ(増やす|減らす)\s*\)\s*$",
    re.IGNORECASE,
)
_FOR_RANGE_RE = re.compile(
    r"^for\s*\(\s*(\w+)\s*を\s*(.+?)\s*から始めて\s*(.+?)\s*を超えない範囲で\s*(.+?)\s*ずつ(増やす|減らす)\s*\)\s*$",
    re.IGNORECASE,
)
_FOR_EACH_RE = re.compile(
    r"^for\s*\(\s*(\w+)\s*に\s*(.+?)\s*の要素を順に代入する\s*\)\s*$",
    re.IGNORECASE,
)
_IF_RE = re.compile(r"^if\s*\((.+)\)\s*$", re.IGNORECASE)
_ELSEIF_RE = re.compile(r"^elseif\s*\((.+)\)\s*$", re.IGNORECASE)
_WHILE_RE = re.compile(r"^while\s*\((.+)\)\s*$", re.IGNORECASE)
_DO_WHILE_RE = re.compile(r"^while\s*\((.+)\)\s*$", re.IGNORECASE)
_RETURN_RE = re.compile(r"^return\s*(?:\(\s*(.+?)\s*\)|\s+(.+))?\s*$", re.IGNORECASE)

# 日本語アクション文
_APPEND_RE = re.compile(r"^(.+?)の末尾\s*に\s*(.+?)\s*(?:の値\s*)?を追加する\s*$")
_SWAP_RE = re.compile(r"^(.+?)と(.+?)の値を入れ替える\s*$")
_INCREMENT_RE = re.compile(r"^(.+?)の値を(\d+)(増やす|減らす)\s*$")
_BREAK_RE = re.compile(r"^(?:(.+?)の行から始まる)?繰返し処理を終了する\s*$")
_PRINT_RE = re.compile(r"^(.+?)を出力する\s*$")
_PRINT_MULTI_RE = re.compile(
    r"^(.+?)の値と(.+?)の値をこの順に(.+?)区切りで出力する\s*$"
)

# 日本語条件式
_JP_COND_UNDEFINED_NOT = re.compile(r"^(.+?)\s*が\s*未定義でない\s*$")
_JP_COND_UNDEFINED = re.compile(r"^(.+?)\s*が\s*未定義\s*$")
_JP_COND_DIVISIBLE = re.compile(r"^(.+?)\s*が\s*(.+?)\s*で割り切れる\s*$")
_JP_COND_NOT_EQUAL = re.compile(r"^(.+?)\s*が\s*(.+?)\s*と等しくない\s*$")
_JP_COND_EQUAL = re.compile(r"^(.+?)\s*が\s*(.+?)\s*と等しい\s*$")
_JP_COND_IKA = re.compile(r"^(.+?)\s*が\s*(.+?)\s*以下\s*$")
_JP_COND_IJOU = re.compile(r"^(.+?)\s*が\s*(.+?)\s*以上\s*$")
_JP_COND_YORI_SMALL = re.compile(r"^(.+?)\s*が\s*(.+?)\s*より小さい\s*$")
_JP_COND_YORI_BIG = re.compile(r"^(.+?)\s*が\s*(.+?)\s*より大きい\s*$")
_JP_COND_DENAI = re.compile(r"^(.+?)\s*が\s*(.+?)\s*でない\s*$")


def parse(source: str) -> Program:
    """擬似言語のソースコードをパースしてASTを返す

    Args:
        source: IPA擬似言語のソースコード

    Returns:
        プログラム全体のAST
    """
    parser = Parser(source)
    return parser.parse()


class Parser:
    """IPA擬似言語の構文解析器"""

    def __init__(self, source: str) -> None:
        self._source = source
        self._lines = self._preprocess(source)
        self._pos = 0

    def parse(self) -> Program:
        """ソースコード全体を解析してASTを生成する"""
        program = Program()
        while not self._at_end():
            line = self._current_line()

            if _FUNC_DEF_RE.match(line):
                program.functions.append(self._parse_function_def())
            elif _GLOBAL_VAR_RE.match(line):
                program.globals.append(self._parse_global_decl())
            else:
                stmt = self._parse_statement()
                if stmt:
                    program.statements.append(stmt)
        return program

    # --- 前処理 ---

    def _preprocess(self, source: str) -> list[str]:
        """ソースコードを行のリストに変換（空行・コメント行を除去）"""
        lines: list[str] = []
        for raw_line in source.split("\n"):
            # 全角スペースを半角スペースに変換（先頭インデント用）
            stripped = raw_line.replace("\u3000", " ").strip()
            # 空行をスキップ
            if not stripped:
                continue
            # 行コメントを除去（行全体がコメントの場合）
            if stripped.startswith("//"):
                continue
            # ブロックコメントを除去（単一行内の場合）
            stripped = re.sub(r"/\*.*?\*/", "", stripped).strip()
            if stripped.startswith("/*"):
                continue
            # インラインコメント // を除去（文字列リテラル外）
            stripped = self._strip_inline_comment(stripped)
            if stripped:
                lines.append(stripped)

        # 行の結合: 波括弧の不均衡がある場合に次の行と結合する
        lines = self._join_continuation_lines(lines)
        return lines

    @staticmethod
    def _strip_inline_comment(line: str) -> str:
        """行末のインラインコメント // を除去する（文字列リテラル内は除く）"""
        in_string = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"':
                in_string = not in_string
            elif not in_string and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                return line[:i].rstrip()
            i += 1
        return line

    @staticmethod
    def _join_continuation_lines(lines: list[str]) -> list[str]:
        """波括弧・丸括弧が閉じていない行を次の行と結合する"""
        result: list[str] = []
        buffer = ""
        brace_depth = 0
        paren_depth = 0
        for line in lines:
            if buffer:
                buffer = buffer + " " + line
            else:
                buffer = line
            for ch in line:
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
                elif ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
            if brace_depth <= 0 and paren_depth <= 0:
                result.append(buffer)
                buffer = ""
                brace_depth = 0
                paren_depth = 0
        if buffer:
            result.append(buffer)
        return result

    # --- ナビゲーション ---

    def _at_end(self) -> bool:
        return self._pos >= len(self._lines)

    def _current_line(self) -> str:
        if self._at_end():
            return ""
        return self._lines[self._pos]

    def _advance_line(self) -> str:
        line = self._current_line()
        self._pos += 1
        return line

    # --- 関数定義 ---

    def _parse_function_def(self) -> FunctionDef:
        """○型名: 関数名(引数) を解析する"""
        line = self._advance_line()
        m = _FUNC_DEF_RE.match(line)
        if not m:
            raise SyntaxError(f"関数定義の解析に失敗しました: {line}")

        return_type = m.group(1)  # None if procedure
        name = m.group(2)
        params_str = m.group(3).strip()
        params = self._parse_params(params_str) if params_str else []
        body = self._parse_block({"endfor", "endwhile"}, is_function_body=True)

        return FunctionDef(name=name, return_type=return_type, params=params, body=body)

    def _parse_params(self, params_str: str) -> list[Parameter]:
        """引数リストを解析する: "整数型: age, 文字列型: name" """
        params: list[Parameter] = []
        for part in params_str.split(","):
            part = part.strip()
            if not part:
                continue
            # "型名: 変数名" or "型名:変数名"
            if ":" in part or "：" in part:
                sep = "：" if "：" in part else ":"
                type_ann, name = part.split(sep, 1)
                params.append(Parameter(name=name.strip(), type_annotation=type_ann.strip()))
            else:
                params.append(Parameter(name=part))
        return params

    # --- グローバル変数 ---

    def _parse_global_decl(self) -> VarDecl:
        """大域: 型名: 変数名 [← 初期値] を解析する"""
        line = self._advance_line()
        m = _GLOBAL_VAR_RE.match(line)
        if not m:
            raise SyntaxError(f"グローバル変数宣言の解析に失敗しました: {line}")
        rest = m.group(1).strip()
        var_decl = self._parse_var_decl_from_text(rest)
        var_decl.is_global = True
        return var_decl

    # --- ブロック解析 ---

    def _parse_block(
        self,
        extra_terminators: set[str] | None = None,
        is_function_body: bool = False,
        stop_at_while: bool = False,
    ) -> list[Any]:
        """ブロック（endif/endfor/endwhile/else/elseif等まで）を解析する"""
        stmts: list[Any] = []
        while not self._at_end():
            line = self._current_line()
            lower = line.lower().strip()

            # ブロック終端キーワード
            if lower in ("endif", "endwhile", "endfor"):
                if not is_function_body:
                    self._advance_line()
                break
            if lower == "else" or lower.startswith("elseif"):
                break

            # do-whileのボディ: while行で停止する
            if stop_at_while and (lower.startswith("while ") or lower.startswith("while(")):
                break

            # 次の関数定義に到達したら終了（関数ボディの場合）
            if is_function_body and line.startswith("○"):
                break

            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)

        return stmts

    # --- 文の解析 ---

    def _parse_statement(self) -> Any | None:
        """1文を解析する"""
        line = self._current_line()
        lower = line.lower().strip()

        # 制御文
        if lower.startswith("if ") or lower.startswith("if("):
            return self._parse_if()
        if lower.startswith("for ") or lower.startswith("for("):
            return self._parse_for()
        if lower.startswith("while ") or lower.startswith("while("):
            return self._parse_while()
        if lower == "do":
            return self._parse_do_while()
        if _RETURN_RE.match(line):
            return self._parse_return()

        # 日本語アクション文（代入より先に判定）
        if m := _APPEND_RE.match(line):
            self._advance_line()
            return AppendStatement(
                target=self._parse_expression(m.group(1)),
                value=self._parse_expression(m.group(2)),
            )
        if m := _SWAP_RE.match(line):
            self._advance_line()
            return SwapStatement(
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _INCREMENT_RE.match(line):
            self._advance_line()
            amount = IntegerLiteral(value=int(m.group(2)))
            if m.group(3) == "減らす":
                amount = UnaryOp(op="-", operand=amount)
            return IncrementStatement(
                target=self._parse_expression(m.group(1)),
                amount=amount,
            )
        if m := _BREAK_RE.match(line):
            self._advance_line()
            return BreakStatement(label=m.group(1))
        if m := _PRINT_MULTI_RE.match(line):
            self._advance_line()
            return PrintStatement(
                values=[
                    self._parse_expression(m.group(1)),
                    self._parse_expression(m.group(2)),
                ],
                separator=m.group(3),
            )
        if m := _PRINT_RE.match(line):
            self._advance_line()
            return PrintStatement(values=[self._parse_expression(m.group(1))])

        # 変数宣言
        if m := _VAR_DECL_RE.match(line):
            # 代入文と区別: 型名には"型"が含まれるか大文字始まりのクラス名
            type_ann = m.group(1).strip()
            if "型" in type_ann or (type_ann[0].isupper() and type_ann.isascii()):
                self._advance_line()
                return self._parse_var_decl_from_text(line)

        # 代入文
        if m := _ASSIGNMENT_RE.match(line):
            self._advance_line()
            return Assignment(
                target=self._parse_expression(m.group(1)),
                value=self._parse_expression(m.group(2)),
            )

        # 式文（関数呼び出し等）
        self._advance_line()
        expr = self._parse_expression(line)
        return ExpressionStatement(expression=expr)

    # --- if文 ---

    def _parse_if(self) -> IfStatement:
        line = self._advance_line()
        m = _IF_RE.match(line)
        if not m:
            raise SyntaxError(f"if文の解析に失敗しました: {line}")

        condition = self._parse_condition(m.group(1))
        then_body = self._parse_block()
        elseif_clauses: list[ElseIfClause] = []
        else_body: list[Any] = []

        while not self._at_end():
            cur = self._current_line()
            if m2 := _ELSEIF_RE.match(cur):
                self._advance_line()
                elseif_cond = self._parse_condition(m2.group(1))
                elseif_body = self._parse_block()
                elseif_clauses.append(
                    ElseIfClause(condition=elseif_cond, body=elseif_body)
                )
            elif cur.lower().strip() == "else":
                self._advance_line()
                else_body = self._parse_block()
            elif cur.lower().strip() == "endif":
                self._advance_line()
                break
            else:
                break

        return IfStatement(
            condition=condition,
            then_body=then_body,
            elseif_clauses=elseif_clauses,
            else_body=else_body,
        )

    # --- for文 ---

    def _parse_for(self) -> ForStatement | ForEachStatement:
        line = self._advance_line()

        # 標準パターン: i を 1 から n まで 1 ずつ増やす
        if m := _FOR_STANDARD_RE.match(line):
            body = self._parse_block()
            return ForStatement(
                var_name=m.group(1),
                start=self._parse_expression(m.group(2)),
                end=self._parse_expression(m.group(3)),
                step=self._parse_expression(m.group(4)),
                direction="increment" if m.group(5) == "増やす" else "decrement",
                body=body,
            )

        # 範囲パターン: i を a から始めて b を超えない範囲で c ずつ増やす
        if m := _FOR_RANGE_RE.match(line):
            body = self._parse_block()
            return ForStatement(
                var_name=m.group(1),
                start=self._parse_expression(m.group(2)),
                end=self._parse_expression(m.group(3)),
                step=self._parse_expression(m.group(4)),
                direction="increment" if m.group(5) == "増やす" else "decrement",
                body=body,
            )

        # for-each: order に orders の要素を順に代入する
        if m := _FOR_EACH_RE.match(line):
            body = self._parse_block()
            return ForEachStatement(
                var_name=m.group(1),
                iterable=self._parse_expression(m.group(2)),
                body=body,
            )

        raise SyntaxError(f"for文の制御記述を解析できません: {line}")

    # --- while文 ---

    def _parse_while(self) -> WhileStatement:
        line = self._advance_line()
        m = _WHILE_RE.match(line)
        if not m:
            raise SyntaxError(f"while文の解析に失敗しました: {line}")
        condition = self._parse_condition(m.group(1))
        body = self._parse_block()
        return WhileStatement(condition=condition, body=body)

    # --- do-while文 ---

    def _parse_do_while(self) -> DoWhileStatement:
        self._advance_line()  # "do" を消費
        body = self._parse_block(stop_at_while=True)
        # while (条件式) を読む
        line = self._current_line()
        m = _DO_WHILE_RE.match(line)
        if not m:
            raise SyntaxError(f"do-while文のwhile部の解析に失敗しました: {line}")
        self._advance_line()
        condition = self._parse_condition(m.group(1))
        return DoWhileStatement(body=body, condition=condition)

    # --- return文 ---

    def _parse_return(self) -> ReturnStatement:
        line = self._advance_line()
        m = _RETURN_RE.match(line)
        if not m:
            return ReturnStatement()
        value_str = m.group(1) or m.group(2)
        if value_str:
            return ReturnStatement(value=self._parse_expression(value_str.strip()))
        return ReturnStatement()

    # --- 変数宣言 ---

    def _parse_var_decl_from_text(self, text: str) -> VarDecl:
        """変数宣言テキストをパースする: "整数型: x, y ← 0" """
        m = _VAR_DECL_RE.match(text)
        if not m:
            raise SyntaxError(f"変数宣言の解析に失敗しました: {text}")

        type_ann = m.group(1).strip()
        rest = m.group(2).strip()

        # "← 初期値" を分離
        initializer = None
        if "←" in rest:
            names_part, init_part = rest.rsplit("←", 1)
            names = [n.strip() for n in names_part.split(",") if n.strip()]
            initializer = self._parse_expression(init_part.strip())
        else:
            names = [n.strip() for n in rest.split(",") if n.strip()]

        return VarDecl(type_annotation=type_ann, names=names, initializer=initializer)

    # --- 条件式の解析 ---

    def _parse_condition(self, text: str) -> Expression:
        """条件式を解析する（日本語パターン＋形式的な式の両対応）"""
        text = text.strip()

        # 複合条件: and/or で分割
        parts = self._split_compound_condition(text)
        if parts:
            op, left_text, right_text = parts
            left = self._parse_condition(left_text)
            right = self._parse_condition(right_text)
            return BinaryOp(op=op, left=left, right=right)

        # 括弧で囲まれた条件
        if text.startswith("(") and text.endswith(")"):
            inner = text[1:-1].strip()
            # 括弧のバランスを確認
            if self._parens_balanced(inner):
                return self._parse_condition(inner)

        # 日本語条件パターン
        jp = self._try_japanese_condition(text)
        if jp:
            return jp

        # 形式的な式として解析
        return self._parse_expression(text)

    def _split_compound_condition(self, text: str) -> tuple[str, str, str] | None:
        """and/or でトップレベル分割を試みる"""
        for keyword in (" and ", " or "):
            depth = 0
            i = 0
            while i < len(text):
                ch = text[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                elif depth == 0 and text[i : i + len(keyword)] == keyword:
                    left = text[:i].strip()
                    right = text[i + len(keyword) :].strip()
                    op = keyword.strip()
                    return (op, left, right)
                i += 1
        return None

    def _parens_balanced(self, text: str) -> bool:
        depth = 0
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth < 0:
                return False
        return depth == 0

    def _try_japanese_condition(self, text: str) -> Expression | None:
        """日本語条件パターンのマッチを試みる"""
        if m := _JP_COND_UNDEFINED_NOT.match(text):
            return BinaryOp(
                op="is not",
                left=self._parse_expression(m.group(1)),
                right=UndefinedLiteral(),
            )
        if m := _JP_COND_UNDEFINED.match(text):
            return BinaryOp(
                op="is",
                left=self._parse_expression(m.group(1)),
                right=UndefinedLiteral(),
            )
        if m := _JP_COND_DIVISIBLE.match(text):
            return BinaryOp(
                op="==",
                left=BinaryOp(
                    op="%",
                    left=self._parse_expression(m.group(1)),
                    right=self._parse_expression(m.group(2)),
                ),
                right=IntegerLiteral(value=0),
            )
        if m := _JP_COND_NOT_EQUAL.match(text):
            return BinaryOp(
                op="!=",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_EQUAL.match(text):
            return BinaryOp(
                op="==",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_IKA.match(text):
            return BinaryOp(
                op="<=",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_IJOU.match(text):
            return BinaryOp(
                op=">=",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_YORI_SMALL.match(text):
            return BinaryOp(
                op="<",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_YORI_BIG.match(text):
            return BinaryOp(
                op=">",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        if m := _JP_COND_DENAI.match(text):
            return BinaryOp(
                op="!=",
                left=self._parse_expression(m.group(1)),
                right=self._parse_expression(m.group(2)),
            )
        return None

    # --- 式の解析 ---

    # 動的配列初期化パターン
    _DYN_ARRAY_1D_RE = re.compile(r"^\{(.+?)個の\s*(.+?)\s*\}$")
    _DYN_ARRAY_2D_RE = re.compile(r"^\{(.+?)行(.+?)列の\s*(.+?)\s*\}$")

    def _parse_expression(self, text: str) -> Expression:
        """テキストから式をパースする"""
        text = text.strip()
        if not text:
            return Identifier(name="")

        # 特殊リテラル
        if text == "未定義の値" or text == "未定義":
            return UndefinedLiteral()
        if text == "−∞" or text == "-∞":
            return NegativeInfinity()

        # 動的配列初期化: {n行m列のX}
        if m := self._DYN_ARRAY_2D_RE.match(text):
            return DynamicArrayInit(
                rows_expr=self._parse_expression(m.group(1)),
                cols_expr=self._parse_expression(m.group(2)),
                init_value=self._parse_expression(m.group(3)),
            )

        # 動的配列初期化: {n個のX}
        if m := self._DYN_ARRAY_1D_RE.match(text):
            return DynamicArrayInit(
                size_expr=self._parse_expression(m.group(1)),
                init_value=self._parse_expression(m.group(2)),
            )

        # トークン化してPrattパーサーで解析
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        # NEWLINE, COMMENT, EOF以外のトークンだけ抽出
        skip_types = (TokenType.NEWLINE, TokenType.COMMENT, TokenType.EOF)
        tokens = [t for t in tokens if t.type not in skip_types]
        if not tokens:
            return Identifier(name=text)

        ep = ExpressionParser(tokens, self)
        return ep.parse()


# --- Pratt式パーサー ---


class ExpressionParser:
    """Prattパーサーによる式の解析"""

    # 演算子優先順位
    PRECEDENCE: dict[TokenType, int] = {
        TokenType.OR: 10,
        TokenType.AND: 20,
        TokenType.EQUAL: 30,
        TokenType.NOT_EQUAL: 30,
        TokenType.LESS_THAN: 30,
        TokenType.GREATER_THAN: 30,
        TokenType.LESS_EQUAL: 30,
        TokenType.GREATER_EQUAL: 30,
        TokenType.PLUS: 40,
        TokenType.MINUS: 40,
        TokenType.MULTIPLY: 50,
        TokenType.DIVIDE: 50,
        TokenType.MOD: 50,
        TokenType.BIT_AND: 25,
        TokenType.BIT_OR: 15,
        TokenType.SHIFT_LEFT: 35,
        TokenType.SHIFT_RIGHT: 35,
        TokenType.DOT: 70,
        TokenType.LBRACKET: 70,
        TokenType.LPAREN: 70,
    }

    # トークン型 → Python演算子文字列
    OP_MAP: dict[TokenType, str] = {
        TokenType.PLUS: "+",
        TokenType.MINUS: "-",
        TokenType.MULTIPLY: "*",
        TokenType.DIVIDE: "/",
        TokenType.MOD: "%",
        TokenType.EQUAL: "==",
        TokenType.NOT_EQUAL: "!=",
        TokenType.LESS_THAN: "<",
        TokenType.GREATER_THAN: ">",
        TokenType.LESS_EQUAL: "<=",
        TokenType.GREATER_EQUAL: ">=",
        TokenType.AND: "and",
        TokenType.OR: "or",
        TokenType.BIT_AND: "&",
        TokenType.BIT_OR: "|",
        TokenType.SHIFT_LEFT: "<<",
        TokenType.SHIFT_RIGHT: ">>",
    }

    def __init__(self, tokens: list[Token], parser: Parser) -> None:
        self._tokens = tokens
        self._pos = 0
        self._parser = parser

    _PROPERTY_SUFFIXES = frozenset(("の要素数", "の文字数", "の行数", "の列数"))

    def parse(self, min_prec: int = 0) -> Expression:
        """演算子優先順位に基づいて式を解析する"""
        left = self._parse_prefix()

        while not self._at_end():
            if self._current_precedence() > min_prec:
                left = self._parse_infix(left)
            elif (
                self._current().type == TokenType.IDENTIFIER
                and self._current().value in self._PROPERTY_SUFFIXES
            ):
                left = self._parse_infix(left)
            else:
                break

        return left

    def _at_end(self) -> bool:
        return self._pos >= len(self._tokens)

    def _current(self) -> Token:
        if self._at_end():
            return Token(TokenType.EOF, "", 0, 0)
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._current()
        self._pos += 1
        return tok

    def _expect(self, token_type: TokenType) -> Token:
        tok = self._current()
        if tok.type != token_type:
            raise SyntaxError(
                f"期待されるトークン: {token_type.name}, 実際: {tok.type.name} ({tok.value!r})"
            )
        return self._advance()

    def _current_precedence(self) -> int:
        if self._at_end():
            return 0
        return self.PRECEDENCE.get(self._current().type, 0)

    def _parse_prefix(self) -> Expression:
        """前置式/アトムを解析する"""
        tok = self._current()

        # 単項演算子
        if tok.type == TokenType.NOT:
            self._advance()
            operand = self.parse(60)
            return UnaryOp(op="not", operand=operand)
        if tok.type in (TokenType.PLUS, TokenType.MINUS):
            self._advance()
            operand = self.parse(60)
            op = "+" if tok.type == TokenType.PLUS else "-"
            return UnaryOp(op=op, operand=operand)

        # 括弧
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self.parse(0)
            self._expect(TokenType.RPAREN)
            return expr

        # 配列リテラル
        if tok.type == TokenType.LBRACE:
            return self._parse_array_literal()

        # リテラル
        if tok.type == TokenType.INTEGER_LITERAL:
            self._advance()
            return IntegerLiteral(value=int(tok.value))
        if tok.type == TokenType.REAL_LITERAL:
            self._advance()
            return RealLiteral(value=float(tok.value))
        if tok.type == TokenType.STRING_LITERAL:
            self._advance()
            return StringLiteral(value=tok.value)
        if tok.type == TokenType.TRUE:
            self._advance()
            return BooleanLiteral(value=True)
        if tok.type == TokenType.FALSE:
            self._advance()
            return BooleanLiteral(value=False)

        # 識別子
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            name = tok.value

            # 未定義の値 / 未定義 → UndefinedLiteral
            if name in ("未定義の値", "未定義"):
                return UndefinedLiteral()

            # 日本語プロパティパターン: Xの要素数, Xの文字数, Xの行数, Xの列数
            for prop_suffix in ("の要素数", "の文字数", "の行数", "の列数"):
                if name.endswith(prop_suffix):
                    obj_name = name[: -len(prop_suffix)]
                    if obj_name:
                        return PropertyAccess(
                            object=Identifier(name=obj_name),
                            property_name=prop_suffix[1:],  # "の" を除去
                        )

            return Identifier(name=name)

        # 解析できない場合
        self._advance()
        return Identifier(name=tok.value)

    def _parse_infix(self, left: Expression) -> Expression:
        """中置式を解析する"""
        tok = self._current()

        # 配列アクセス: expr[index]
        if tok.type == TokenType.LBRACKET:
            self._advance()
            indices: list[Expression] = [self.parse(0)]
            while not self._at_end() and self._current().type == TokenType.COMMA:
                self._advance()
                indices.append(self.parse(0))
            self._expect(TokenType.RBRACKET)
            return ArrayAccess(array=left, indices=indices)

        # 関数呼び出し: expr(args)
        if tok.type == TokenType.LPAREN:
            self._advance()
            args: list[Expression] = []
            if self._current().type != TokenType.RPAREN:
                args.append(self.parse(0))
                while not self._at_end() and self._current().type == TokenType.COMMA:
                    self._advance()
                    args.append(self.parse(0))
            self._expect(TokenType.RPAREN)
            return FunctionCall(function=left, arguments=args)

        # メンバアクセス: expr.member
        if tok.type == TokenType.DOT:
            self._advance()
            member_tok = self._expect(TokenType.IDENTIFIER)
            return MemberAccess(object=left, member=member_tok.value)

        # 日本語プロパティ後置: expr の要素数, expr の文字数, etc.
        if tok.type == TokenType.IDENTIFIER:
            for prop_suffix in ("の要素数", "の文字数", "の行数", "の列数"):
                if tok.value == prop_suffix:
                    self._advance()
                    return PropertyAccess(
                        object=left,
                        property_name=prop_suffix[1:],  # "の" を除去
                    )

        # 二項演算子
        if tok.type in self.OP_MAP:
            prec = self.PRECEDENCE.get(tok.type, 0)
            self._advance()
            right = self.parse(prec)
            op = self.OP_MAP[tok.type]
            # ÷ Xの商 → 整数除算 (//), ÷ X の余り → 剰余 (%)
            if tok.type == TokenType.DIVIDE:
                if not self._at_end() and self._current().type == TokenType.IDENTIFIER:
                    if self._current().value == "の商":
                        self._advance()
                        op = "//"
                    elif self._current().value == "の余り":
                        self._advance()
                        op = "%"
            return BinaryOp(op=op, left=left, right=right)

        # 解析できない場合はそのまま返す
        return left

    def _parse_array_literal(self) -> ArrayLiteral:
        """配列リテラル: {1, 2, 3} or {{1,2},{3,4}}"""
        self._expect(TokenType.LBRACE)
        elements: list[Expression] = []

        if self._current().type != TokenType.RBRACE:
            elements.append(self._parse_array_element())
            while not self._at_end() and self._current().type == TokenType.COMMA:
                self._advance()
                if self._current().type == TokenType.RBRACE:
                    break
                elements.append(self._parse_array_element())

        self._expect(TokenType.RBRACE)
        return ArrayLiteral(elements=elements)

    def _parse_array_element(self) -> Expression:
        """配列リテラルの1要素（ネスト対応）"""
        if self._current().type == TokenType.LBRACE:
            return self._parse_array_literal()
        return self.parse(0)
