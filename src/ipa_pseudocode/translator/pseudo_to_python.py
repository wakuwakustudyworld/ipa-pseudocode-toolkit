"""擬似言語→Python変換器

ASTを走査してPythonコードを生成するトランスレータ。
"""

from __future__ import annotations

from typing import Any

from ..parser.ast_nodes import (
    AppendStatement,
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOp,
    BooleanLiteral,
    BreakStatement,
    CharAt,
    DoWhileStatement,
    DynamicArrayInit,
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
from .codegen import CodeBuilder


def translate(program: Program) -> str:
    """プログラムASTをPythonコードに変換する

    Args:
        program: パース済みのプログラムAST

    Returns:
        Pythonソースコード文字列
    """
    translator = PseudoToPythonTranslator()
    return translator.translate(program)


class PseudoToPythonTranslator:
    """AST→Pythonコード変換器"""

    def __init__(self) -> None:
        self._builder = CodeBuilder()

    def translate(self, program: Program) -> str:
        """プログラム全体を変換する"""
        # グローバル変数
        for stmt in program.globals:
            self._translate_statement(stmt)
        if program.globals:
            self._builder.add_blank_line()

        # 関数定義
        for func in program.functions:
            self._translate_function(func)
            self._builder.add_blank_line()

        # トップレベル文
        for stmt in program.statements:
            self._translate_statement(stmt)

        return self._builder.build()

    # --- 関数定義 ---

    def _translate_function(self, func: FunctionDef) -> None:
        params = ", ".join(p.name for p in func.params)
        self._builder.add_line(f"def {func.name}({params}):")
        self._builder.indent()
        if not func.body:
            self._builder.add_line("pass")
        else:
            for stmt in func.body:
                self._translate_statement(stmt)
        self._builder.dedent()

    # --- 文の変換 ---

    def _translate_statement(self, stmt: Any) -> None:
        if isinstance(stmt, VarDecl):
            self._translate_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self._translate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._translate_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self._translate_while(stmt)
        elif isinstance(stmt, DoWhileStatement):
            self._translate_do_while(stmt)
        elif isinstance(stmt, ForStatement):
            self._translate_for(stmt)
        elif isinstance(stmt, ForEachStatement):
            self._translate_for_each(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._translate_return(stmt)
        elif isinstance(stmt, BreakStatement):
            self._builder.add_line("break")
        elif isinstance(stmt, PrintStatement):
            self._translate_print(stmt)
        elif isinstance(stmt, SwapStatement):
            self._translate_swap(stmt)
        elif isinstance(stmt, AppendStatement):
            self._translate_append(stmt)
        elif isinstance(stmt, IncrementStatement):
            self._translate_increment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._builder.add_line(self._expr(stmt.expression))

    def _translate_var_decl(self, decl: VarDecl) -> None:
        if decl.initializer:
            init = self._expr(decl.initializer)
            if len(decl.names) == 1:
                self._builder.add_line(f"{decl.names[0]} = {init}")
            else:
                # 最後の変数に初期値、他はNone
                for name in decl.names[:-1]:
                    self._builder.add_line(f"{name} = None")
                self._builder.add_line(f"{decl.names[-1]} = {init}")
        else:
            for name in decl.names:
                self._builder.add_line(f"{name} = None")

    def _translate_assignment(self, assign: Assignment) -> None:
        target = self._expr(assign.target)
        value = self._expr(assign.value)
        self._builder.add_line(f"{target} = {value}")

    def _translate_if(self, stmt: IfStatement) -> None:
        self._builder.add_line(f"if {self._expr(stmt.condition)}:")
        self._builder.indent()
        if not stmt.then_body:
            self._builder.add_line("pass")
        else:
            for s in stmt.then_body:
                self._translate_statement(s)
        self._builder.dedent()

        for clause in stmt.elseif_clauses:
            self._builder.add_line(f"elif {self._expr(clause.condition)}:")
            self._builder.indent()
            if not clause.body:
                self._builder.add_line("pass")
            else:
                for s in clause.body:
                    self._translate_statement(s)
            self._builder.dedent()

        if stmt.else_body:
            self._builder.add_line("else:")
            self._builder.indent()
            for s in stmt.else_body:
                self._translate_statement(s)
            self._builder.dedent()

    def _translate_while(self, stmt: WhileStatement) -> None:
        self._builder.add_line(f"while {self._expr(stmt.condition)}:")
        self._builder.indent()
        if not stmt.body:
            self._builder.add_line("pass")
        else:
            for s in stmt.body:
                self._translate_statement(s)
        self._builder.dedent()

    def _translate_do_while(self, stmt: DoWhileStatement) -> None:
        self._builder.add_line("while True:")
        self._builder.indent()
        for s in stmt.body:
            self._translate_statement(s)
        self._builder.add_line(f"if not ({self._expr(stmt.condition)}):")
        self._builder.indent()
        self._builder.add_line("break")
        self._builder.dedent()
        self._builder.dedent()

    def _translate_for(self, stmt: ForStatement) -> None:
        start = self._expr(stmt.start)
        end = self._expr(stmt.end)
        step = self._expr(stmt.step)

        if stmt.direction == "increment":
            if step == "1":
                self._builder.add_line(f"for {stmt.var_name} in range({start}, {end} + 1):")
            else:
                self._builder.add_line(
                    f"for {stmt.var_name} in range({start}, {end} + 1, {step}):"
                )
        else:  # decrement
            if step == "1":
                self._builder.add_line(
                    f"for {stmt.var_name} in range({start}, {end} - 1, -1):"
                )
            else:
                self._builder.add_line(
                    f"for {stmt.var_name} in range({start}, {end} - 1, -{step}):"
                )

        self._builder.indent()
        if not stmt.body:
            self._builder.add_line("pass")
        else:
            for s in stmt.body:
                self._translate_statement(s)
        self._builder.dedent()

    def _translate_for_each(self, stmt: ForEachStatement) -> None:
        self._builder.add_line(f"for {stmt.var_name} in {self._expr(stmt.iterable)}:")
        self._builder.indent()
        if not stmt.body:
            self._builder.add_line("pass")
        else:
            for s in stmt.body:
                self._translate_statement(s)
        self._builder.dedent()

    def _translate_return(self, stmt: ReturnStatement) -> None:
        if stmt.value:
            self._builder.add_line(f"return {self._expr(stmt.value)}")
        else:
            self._builder.add_line("return")

    def _translate_print(self, stmt: PrintStatement) -> None:
        values = ", ".join(self._expr(v) for v in stmt.values)
        if stmt.separator == "コンマ" or stmt.separator == "カンマ":
            self._builder.add_line(f'print({values}, sep=",")')
        elif stmt.separator == "空白":
            self._builder.add_line(f'print({values}, sep=" ")')
        elif stmt.separator:
            self._builder.add_line(f'print({values}, sep="{stmt.separator}")')
        else:
            self._builder.add_line(f"print({values})")

    def _translate_swap(self, stmt: SwapStatement) -> None:
        left = self._expr(stmt.left)
        right = self._expr(stmt.right)
        self._builder.add_line(f"{left}, {right} = {right}, {left}")

    def _translate_append(self, stmt: AppendStatement) -> None:
        target = self._expr(stmt.target)
        value = self._expr(stmt.value)
        self._builder.add_line(f"{target}.append({value})")

    def _translate_increment(self, stmt: IncrementStatement) -> None:
        target = self._expr(stmt.target)
        amount = self._expr(stmt.amount)
        self._builder.add_line(f"{target} += {amount}")

    # --- 式の変換 ---

    def _expr(self, expr: Expression) -> str:
        """式をPythonコード文字列に変換する"""
        if isinstance(expr, IntegerLiteral):
            return str(expr.value)
        if isinstance(expr, RealLiteral):
            return str(expr.value)
        if isinstance(expr, StringLiteral):
            return repr(expr.value)
        if isinstance(expr, BooleanLiteral):
            return "True" if expr.value else "False"
        if isinstance(expr, UndefinedLiteral):
            return "None"
        if isinstance(expr, NegativeInfinity):
            return "float('-inf')"
        if isinstance(expr, Identifier):
            return expr.name
        if isinstance(expr, ArrayLiteral):
            elements = ", ".join(self._expr(e) for e in expr.elements)
            return f"[{elements}]"
        if isinstance(expr, ArrayAccess):
            array = self._expr(expr.array)
            indices = ", ".join(self._expr(i) for i in expr.indices)
            return f"{array}[{indices}]"
        if isinstance(expr, MemberAccess):
            obj = self._expr(expr.object)
            return f"{obj}.{expr.member}"
        if isinstance(expr, FunctionCall):
            func = self._expr(expr.function)
            args = ", ".join(self._expr(a) for a in expr.arguments)
            return f"{func}({args})"
        if isinstance(expr, BinaryOp):
            left = self._expr(expr.left)
            right = self._expr(expr.right)
            op = expr.op
            if op == "is":
                return f"{left} is {right}"
            if op == "is not":
                return f"{left} is not {right}"
            return f"{left} {op} {right}"
        if isinstance(expr, UnaryOp):
            operand = self._expr(expr.operand)
            if expr.op == "not":
                return f"not {operand}"
            return f"{expr.op}{operand}"
        if isinstance(expr, PropertyAccess):
            obj = self._expr(expr.object)
            prop = expr.property_name
            if prop in ("要素数", "文字数"):
                return f"len({obj})"
            if prop == "行数":
                return f"{obj}.rows"
            if prop == "列数":
                return f"{obj}.cols"
            return f"{obj}.{prop}"
        if isinstance(expr, CharAt):
            s = self._expr(expr.string)
            idx = self._expr(expr.index)
            return f"{s}[{idx} - 1]"
        if isinstance(expr, DynamicArrayInit):
            init_val = self._expr(expr.init_value)
            if expr.rows_expr and expr.cols_expr:
                rows = self._expr(expr.rows_expr)
                cols = self._expr(expr.cols_expr)
                return f"[[{init_val}] * {cols} for _ in range({rows})]"
            if expr.size_expr:
                size = self._expr(expr.size_expr)
                return f"[{init_val}] * {size}"
            return f"[{init_val}]"
        # フォールバック
        return str(expr)
