"""ASTノード定義

IPA擬似言語の抽象構文木（AST）を構成するノードクラスを定義する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

# --- 基底 ---


@dataclass
class ASTNode:
    """AST基底ノード"""

    line: int = 0
    column: int = 0


# --- 式（Expression）---


@dataclass
class Expression(ASTNode):
    """式の基底"""


@dataclass
class IntegerLiteral(Expression):
    """整数リテラル"""

    value: int = 0


@dataclass
class RealLiteral(Expression):
    """実数リテラル"""

    value: float = 0.0


@dataclass
class StringLiteral(Expression):
    """文字列リテラル"""

    value: str = ""


@dataclass
class BooleanLiteral(Expression):
    """論理型定数（true/false）"""

    value: bool = False


@dataclass
class UndefinedLiteral(Expression):
    """未定義 / 未定義の値"""


@dataclass
class NegativeInfinity(Expression):
    """−∞"""


@dataclass
class Identifier(Expression):
    """識別子"""

    name: str = ""


@dataclass
class ArrayLiteral(Expression):
    """{1, 2, 3} や {{1,2},{3,4}} のような配列リテラル"""

    elements: list[Expression] = field(default_factory=list)


@dataclass
class ArrayAccess(Expression):
    """配列アクセス: arr[i] または arr[i, j]"""

    array: Expression = field(default_factory=Expression)
    indices: list[Expression] = field(default_factory=list)


@dataclass
class MemberAccess(Expression):
    """メンバアクセス: obj.member"""

    object: Expression = field(default_factory=Expression)
    member: str = ""


@dataclass
class FunctionCall(Expression):
    """関数/手続き呼び出し: func(args) または obj.method(args)"""

    function: Expression = field(default_factory=Expression)
    arguments: list[Expression] = field(default_factory=list)


@dataclass
class BinaryOp(Expression):
    """二項演算"""

    op: str = ""  # "+", "-", "*", "/", "//", "%", "==", "!=", etc.
    left: Expression = field(default_factory=Expression)
    right: Expression = field(default_factory=Expression)


@dataclass
class UnaryOp(Expression):
    """単項演算"""

    op: str = ""  # "not", "+", "-"
    operand: Expression = field(default_factory=Expression)


@dataclass
class PropertyAccess(Expression):
    """日本語プロパティ風アクセス: arrayの要素数, binaryの文字数 等"""

    object: Expression = field(default_factory=Expression)
    property_name: str = ""  # "要素数", "文字数", "行数", "列数"


@dataclass
class CharAt(Expression):
    """文字アクセス: binaryのi文字目の文字"""

    string: Expression = field(default_factory=Expression)
    index: Expression = field(default_factory=Expression)


@dataclass
class DynamicArrayInit(Expression):
    """{5個の0} や {nodeNum行nodeNum列の0} のような動的配列初期化"""

    size_expr: Expression | None = None  # 1D: 要素数
    rows_expr: Expression | None = None  # 2D: 行数
    cols_expr: Expression | None = None  # 2D: 列数
    init_value: Expression = field(default_factory=Expression)


# --- 文（Statement）---

# Statementは以下のいずれかのノード型
Statement = Union[
    "VarDecl",
    "Assignment",
    "IfStatement",
    "WhileStatement",
    "DoWhileStatement",
    "ForStatement",
    "ForEachStatement",
    "ReturnStatement",
    "BreakStatement",
    "PrintStatement",
    "SwapStatement",
    "AppendStatement",
    "IncrementStatement",
    "ExpressionStatement",
]


@dataclass
class VarDecl(ASTNode):
    """変数宣言: 型名: 変数名 [← 初期値]"""

    type_annotation: str = ""
    names: list[str] = field(default_factory=list)
    initializer: Expression | None = None
    is_global: bool = False


@dataclass
class Assignment(ASTNode):
    """代入文: 変数名 ← 式"""

    target: Expression = field(default_factory=Expression)
    value: Expression = field(default_factory=Expression)


@dataclass
class ElseIfClause(ASTNode):
    """elseif節"""

    condition: Expression = field(default_factory=Expression)
    body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class IfStatement(ASTNode):
    """if文: if (条件式) ... elseif ... else ... endif"""

    condition: Expression = field(default_factory=Expression)
    then_body: list[Any] = field(default_factory=list)  # list[Statement]
    elseif_clauses: list[ElseIfClause] = field(default_factory=list)
    else_body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class WhileStatement(ASTNode):
    """while文: while (条件式) ... endwhile"""

    condition: Expression = field(default_factory=Expression)
    body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class DoWhileStatement(ASTNode):
    """do-while文: do ... while (条件式)"""

    body: list[Any] = field(default_factory=list)  # list[Statement]
    condition: Expression = field(default_factory=Expression)


@dataclass
class ForStatement(ASTNode):
    """for文: for (iを1からnまで1ずつ増やす) ... endfor"""

    var_name: str = ""
    start: Expression = field(default_factory=Expression)
    end: Expression = field(default_factory=Expression)
    step: Expression = field(default_factory=Expression)
    direction: str = "increment"  # "increment" or "decrement"
    body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class ForEachStatement(ASTNode):
    """for-each文: for (orderにordersの要素を順に代入する) ... endfor"""

    var_name: str = ""
    iterable: Expression = field(default_factory=Expression)
    body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class ReturnStatement(ASTNode):
    """return文"""

    value: Expression | None = None


@dataclass
class BreakStatement(ASTNode):
    """繰返し処理を終了する（break）"""

    label: str | None = None


@dataclass
class PrintStatement(ASTNode):
    """出力文"""

    values: list[Expression] = field(default_factory=list)
    separator: str = ""


@dataclass
class SwapStatement(ASTNode):
    """値の入れ替え: data[i]とdata[j]の値を入れ替える"""

    left: Expression = field(default_factory=Expression)
    right: Expression = field(default_factory=Expression)


@dataclass
class AppendStatement(ASTNode):
    """末尾追加: pnListの末尾にiの値を追加する"""

    target: Expression = field(default_factory=Expression)
    value: Expression = field(default_factory=Expression)


@dataclass
class IncrementStatement(ASTNode):
    """値の増減: itemCountの値を1増やす"""

    target: Expression = field(default_factory=Expression)
    amount: Expression = field(default_factory=Expression)


@dataclass
class ExpressionStatement(ASTNode):
    """式文（関数呼び出し等）"""

    expression: Expression = field(default_factory=Expression)


# --- プログラム構造 ---


@dataclass
class Parameter(ASTNode):
    """関数の仮引数"""

    name: str = ""
    type_annotation: str = ""


@dataclass
class FunctionDef(ASTNode):
    """関数/手続き定義: ○型名: 関数名(引数)"""

    name: str = ""
    return_type: str | None = None
    params: list[Parameter] = field(default_factory=list)
    body: list[Any] = field(default_factory=list)  # list[Statement]


@dataclass
class Program(ASTNode):
    """プログラム全体"""

    functions: list[FunctionDef] = field(default_factory=list)
    globals: list[Any] = field(default_factory=list)  # list[Statement] (global decls)
    statements: list[Any] = field(default_factory=list)  # list[Statement]
