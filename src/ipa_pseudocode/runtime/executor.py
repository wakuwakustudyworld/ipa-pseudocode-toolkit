"""擬似言語コード実行エンジン

ASTを直接走査して擬似言語プログラムを実行する。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from ..core.array import Array, Array2D
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
from .builtins import BUILTIN_FUNCTIONS
from .trace import TraceTable, Tracer


class _ReturnSignal(Exception):
    """関数からの return を伝搬するシグナル"""

    def __init__(self, value: Any = None) -> None:
        self.value = value


class _BreakSignal(Exception):
    """ループからの break を伝搬するシグナル"""

    def __init__(self, label: str | None = None) -> None:
        self.label = label


@dataclass
class ExecutionResult:
    """実行結果"""

    output: list[str] = field(default_factory=list)
    return_value: Any = None
    trace: TraceTable | None = None
    global_vars: dict[str, Any] = field(default_factory=dict)


class Executor:
    """擬似言語AST実行エンジン"""

    def __init__(
        self,
        trace_enabled: bool = False,
        max_steps: int = 100_000,
    ) -> None:
        self._global_scope: dict[str, Any] = {}
        self._call_stack: list[dict[str, Any]] = []
        self._functions: dict[str, FunctionDef] = {}
        self._output: list[str] = []
        self._step_count: int = 0
        self._max_steps: int = max_steps

        # トレース
        self._trace_enabled = trace_enabled
        self._tracer: Tracer | None = Tracer() if trace_enabled else None

    # === 公開 API ===

    def execute(self, program: Program) -> ExecutionResult:
        """プログラム全体を実行する"""
        # 関数テーブルに登録
        for func in program.functions:
            self._functions[func.name] = func

        # グローバル変数を初期化
        for stmt in program.globals:
            self._exec_stmt(stmt)

        # トップレベル文を実行
        return_value = None
        try:
            for stmt in program.statements:
                self._exec_stmt(stmt)
        except _ReturnSignal as sig:
            return_value = sig.value

        trace_table = None
        if self._tracer:
            trace_table = self._tracer.build_table()

        return ExecutionResult(
            output=list(self._output),
            return_value=return_value,
            trace=trace_table,
            global_vars=dict(self._global_scope),
        )

    def call_function(self, name: str, *args: Any) -> Any:
        """登録済みの関数を呼び出す"""
        if name not in self._functions:
            raise RuntimeError(f"関数 '{name}' が定義されていません")
        return self._call_user_function(name, list(args))

    # === スコープ管理 ===

    def _current_scope(self) -> dict[str, Any]:
        """現在のスコープ（ローカルがあればローカル、なければグローバル）"""
        if self._call_stack:
            return self._call_stack[-1]
        return self._global_scope

    def _get_var(self, name: str) -> Any:
        """変数を読み取る（ローカル→グローバルの順に探索）"""
        if self._call_stack:
            local = self._call_stack[-1]
            if name in local:
                return local[name]
        if name in self._global_scope:
            return self._global_scope[name]
        raise RuntimeError(f"変数 '{name}' が定義されていません")

    def _set_var(self, name: str, value: Any) -> None:
        """変数に値を設定する"""
        # グローバル変数が存在し、ローカルに同名がなければグローバルを更新
        if self._call_stack:
            local = self._call_stack[-1]
            if name in local:
                local[name] = value
                return
            if name in self._global_scope:
                self._global_scope[name] = value
                return
            # ローカル変数として設定
            local[name] = value
        else:
            self._global_scope[name] = value

    def _current_scope_name(self) -> str:
        """トレース用の現在スコープ名"""
        if self._call_stack:
            return self._call_stack[-1].get("__func_name__", "local")
        return "global"

    def _all_visible_vars(self) -> dict[str, Any]:
        """トレース用：現在見えている全変数"""
        result = dict(self._global_scope)
        if self._call_stack:
            local = self._call_stack[-1]
            result.update({k: v for k, v in local.items() if not k.startswith("__")})
        return result

    # === ステップカウント ===

    def _tick(self) -> None:
        """ステップカウントを増やし、上限チェック"""
        self._step_count += 1
        if self._step_count > self._max_steps:
            raise RuntimeError(
                f"最大ステップ数（{self._max_steps}）を超えました。無限ループの可能性があります"
            )

    # === トレース記録 ===

    def _trace(
        self,
        description: str,
        event: str,
        detail: str = "",
        output: str | None = None,
    ) -> None:
        """トレースが有効な場合に記録する"""
        if self._tracer:
            self._tracer.record(
                description=description,
                variables=self._all_visible_vars(),
                scope=self._current_scope_name(),
                event=event,
                detail=detail,
                output=output,
            )

    # === 文の実行 ===

    def _exec_stmt(self, stmt: Any) -> None:
        self._tick()
        if isinstance(stmt, VarDecl):
            self._exec_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self._exec_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._exec_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self._exec_while(stmt)
        elif isinstance(stmt, DoWhileStatement):
            self._exec_do_while(stmt)
        elif isinstance(stmt, ForStatement):
            self._exec_for(stmt)
        elif isinstance(stmt, ForEachStatement):
            self._exec_for_each(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._exec_return(stmt)
        elif isinstance(stmt, BreakStatement):
            self._exec_break(stmt)
        elif isinstance(stmt, PrintStatement):
            self._exec_print(stmt)
        elif isinstance(stmt, SwapStatement):
            self._exec_swap(stmt)
        elif isinstance(stmt, AppendStatement):
            self._exec_append(stmt)
        elif isinstance(stmt, IncrementStatement):
            self._exec_increment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._eval_expr(stmt.expression)

    def _exec_var_decl(self, decl: VarDecl) -> None:
        """変数宣言"""
        scope = self._global_scope if (not self._call_stack or decl.is_global) else self._call_stack[-1]
        if decl.initializer:
            init_val = self._eval_expr(decl.initializer)
            if len(decl.names) == 1:
                scope[decl.names[0]] = init_val
                self._trace(f"{decl.names[0]} ← {_repr(init_val)}", "assign")
            else:
                for name in decl.names[:-1]:
                    scope[name] = None
                scope[decl.names[-1]] = init_val
                self._trace(
                    f"{', '.join(decl.names)} 宣言（{decl.names[-1]} ← {_repr(init_val)}）",
                    "assign",
                )
        else:
            for name in decl.names:
                scope[name] = None
            self._trace(f"{', '.join(decl.names)} 宣言（未定義）", "assign")

    def _exec_assignment(self, assign: Assignment) -> None:
        """代入文"""
        value = self._eval_expr(assign.value)
        self._assign_target(assign.target, value)
        self._trace(f"{_expr_desc(assign.target)} ← {_repr(value)}", "assign")

    def _assign_target(self, target: Expression, value: Any) -> None:
        """代入先に値を設定する"""
        if isinstance(target, Identifier):
            self._set_var(target.name, value)
        elif isinstance(target, ArrayAccess):
            arr = self._eval_expr(target.array)
            indices = [self._eval_expr(i) for i in target.indices]
            if len(indices) == 1:
                arr[indices[0]] = value
            elif len(indices) == 2:
                arr[indices[0], indices[1]] = value
        elif isinstance(target, MemberAccess):
            obj = self._eval_expr(target.object)
            setattr(obj, target.member, value)
        else:
            raise RuntimeError(f"代入先として無効な式です: {type(target).__name__}")

    def _exec_if(self, stmt: IfStatement) -> None:
        """if文"""
        cond = self._eval_expr(stmt.condition)
        if cond:
            self._trace(f"if ({_expr_desc(stmt.condition)})", "branch", "→ true")
            for s in stmt.then_body:
                self._exec_stmt(s)
            return

        for clause in stmt.elseif_clauses:
            cond = self._eval_expr(clause.condition)
            if cond:
                self._trace(
                    f"elseif ({_expr_desc(clause.condition)})", "branch", "→ true"
                )
                for s in clause.body:
                    self._exec_stmt(s)
                return

        if stmt.else_body:
            self._trace("else", "branch")
            for s in stmt.else_body:
                self._exec_stmt(s)

    def _exec_while(self, stmt: WhileStatement) -> None:
        """while文"""
        while True:
            cond = self._eval_expr(stmt.condition)
            if not cond:
                break
            self._trace(f"while ({_expr_desc(stmt.condition)})", "loop", "→ true")
            try:
                for s in stmt.body:
                    self._exec_stmt(s)
            except _BreakSignal as sig:
                if sig.label is None:
                    break
                raise

    def _exec_do_while(self, stmt: DoWhileStatement) -> None:
        """do-while文"""
        while True:
            self._trace("do", "loop")
            try:
                for s in stmt.body:
                    self._exec_stmt(s)
            except _BreakSignal as sig:
                if sig.label is None:
                    break
                raise
            cond = self._eval_expr(stmt.condition)
            if not cond:
                break

    def _exec_for(self, stmt: ForStatement) -> None:
        """for文"""
        start = self._eval_expr(stmt.start)
        end = self._eval_expr(stmt.end)
        step = self._eval_expr(stmt.step)
        scope = self._current_scope()

        if stmt.direction == "increment":
            i = start
            while i <= end:
                scope[stmt.var_name] = i
                self._trace(
                    f"for {stmt.var_name} = {i}", "loop",
                )
                try:
                    for s in stmt.body:
                        self._exec_stmt(s)
                except _BreakSignal as sig:
                    if sig.label is None:
                        break
                    raise
                i += step
        else:  # decrement
            i = start
            while i >= end:
                scope[stmt.var_name] = i
                self._trace(
                    f"for {stmt.var_name} = {i}", "loop",
                )
                try:
                    for s in stmt.body:
                        self._exec_stmt(s)
                except _BreakSignal as sig:
                    if sig.label is None:
                        break
                    raise
                i -= step

    def _exec_for_each(self, stmt: ForEachStatement) -> None:
        """for-each文"""
        iterable = self._eval_expr(stmt.iterable)
        scope = self._current_scope()
        for item in iterable:
            scope[stmt.var_name] = item
            self._trace(f"for {stmt.var_name} = {_repr(item)}", "loop")
            try:
                for s in stmt.body:
                    self._exec_stmt(s)
            except _BreakSignal as sig:
                if sig.label is None:
                    break
                raise

    def _exec_return(self, stmt: ReturnStatement) -> None:
        """return文"""
        value = self._eval_expr(stmt.value) if stmt.value else None
        self._trace(f"return {_repr(value)}", "return")
        raise _ReturnSignal(value)

    def _exec_break(self, stmt: BreakStatement) -> None:
        """break文"""
        self._trace("break", "branch", f"label={stmt.label}" if stmt.label else "")
        raise _BreakSignal(stmt.label)

    def _exec_print(self, stmt: PrintStatement) -> None:
        """出力文"""
        values = [self._eval_expr(v) for v in stmt.values]
        str_values = [str(v) for v in values]

        if stmt.separator in ("コンマ", "カンマ"):
            sep = ","
        elif stmt.separator == "空白":
            sep = " "
        elif stmt.separator:
            sep = stmt.separator
        else:
            sep = " "

        output_str = sep.join(str_values)
        self._output.append(output_str)
        self._trace(f"出力: {output_str}", "output", output=output_str)

    def _exec_swap(self, stmt: SwapStatement) -> None:
        """値の入れ替え"""
        left_val = self._eval_expr(stmt.left)
        right_val = self._eval_expr(stmt.right)
        self._assign_target(stmt.left, right_val)
        self._assign_target(stmt.right, left_val)
        self._trace(
            f"{_expr_desc(stmt.left)} ↔ {_expr_desc(stmt.right)}", "assign"
        )

    def _exec_append(self, stmt: AppendStatement) -> None:
        """末尾追加"""
        target = self._eval_expr(stmt.target)
        value = self._eval_expr(stmt.value)
        target.append(value)
        self._trace(
            f"{_expr_desc(stmt.target)}の末尾に{_repr(value)}を追加", "assign"
        )

    def _exec_increment(self, stmt: IncrementStatement) -> None:
        """値の増減"""
        current = self._eval_expr(stmt.target)
        amount = self._eval_expr(stmt.amount)
        new_value = current + amount
        self._assign_target(stmt.target, new_value)
        self._trace(
            f"{_expr_desc(stmt.target)} += {_repr(amount)} → {_repr(new_value)}",
            "assign",
        )

    # === 式の評価 ===

    def _eval_expr(self, expr: Expression) -> Any:
        if isinstance(expr, IntegerLiteral):
            return expr.value
        if isinstance(expr, RealLiteral):
            return expr.value
        if isinstance(expr, StringLiteral):
            return expr.value
        if isinstance(expr, BooleanLiteral):
            return expr.value
        if isinstance(expr, UndefinedLiteral):
            return None
        if isinstance(expr, NegativeInfinity):
            return float("-inf")
        if isinstance(expr, Identifier):
            return self._get_var(expr.name)
        if isinstance(expr, ArrayLiteral):
            return self._eval_array_literal(expr)
        if isinstance(expr, ArrayAccess):
            return self._eval_array_access(expr)
        if isinstance(expr, MemberAccess):
            return self._eval_member_access(expr)
        if isinstance(expr, FunctionCall):
            return self._eval_function_call(expr)
        if isinstance(expr, BinaryOp):
            return self._eval_binary_op(expr)
        if isinstance(expr, UnaryOp):
            return self._eval_unary_op(expr)
        if isinstance(expr, PropertyAccess):
            return self._eval_property_access(expr)
        if isinstance(expr, CharAt):
            return self._eval_char_at(expr)
        if isinstance(expr, DynamicArrayInit):
            return self._eval_dynamic_array_init(expr)
        raise RuntimeError(f"未対応の式ノードです: {type(expr).__name__}")

    def _eval_array_literal(self, expr: ArrayLiteral) -> Array:
        """配列リテラル"""
        elements = [self._eval_expr(e) for e in expr.elements]
        # ネスト配列かどうか判定
        if elements and isinstance(elements[0], Array):
            # Array の配列 → Array2D に変換
            rows = [el.to_list() for el in elements]
            return Array2D.from_literal(rows)
        return Array.from_literal(elements)

    def _eval_array_access(self, expr: ArrayAccess) -> Any:
        """配列アクセス"""
        arr = self._eval_expr(expr.array)
        indices = [self._eval_expr(i) for i in expr.indices]
        if len(indices) == 1:
            return arr[indices[0]]
        if len(indices) == 2:
            return arr[indices[0], indices[1]]
        raise RuntimeError(f"3次元以上の配列アクセスには対応していません")

    def _eval_member_access(self, expr: MemberAccess) -> Any:
        """メンバアクセス"""
        obj = self._eval_expr(expr.object)
        return getattr(obj, expr.member)

    def _eval_function_call(self, expr: FunctionCall) -> Any:
        """関数呼び出し"""
        args = [self._eval_expr(a) for a in expr.arguments]

        # 関数名を取得
        if isinstance(expr.function, Identifier):
            name = expr.function.name
            # 組込み関数
            if name in BUILTIN_FUNCTIONS:
                return BUILTIN_FUNCTIONS[name](*args)
            # ユーザー定義関数
            if name in self._functions:
                return self._call_user_function(name, args)
            raise RuntimeError(f"関数 '{name}' が定義されていません")

        if isinstance(expr.function, MemberAccess):
            obj = self._eval_expr(expr.function.object)
            method = getattr(obj, expr.function.member)
            return method(*args)

        # 式として評価可能な関数
        func = self._eval_expr(expr.function)
        return func(*args)

    def _call_user_function(self, name: str, args: list[Any]) -> Any:
        """ユーザー定義関数を呼び出す"""
        func_def = self._functions[name]
        local_scope: dict[str, Any] = {"__func_name__": name}

        # 仮引数にバインド
        for param, arg_val in zip(func_def.params, args):
            local_scope[param.name] = arg_val

        self._call_stack.append(local_scope)
        self._trace(
            f"{name}({', '.join(_repr(a) for a in args)}) 呼び出し",
            "call",
        )

        try:
            for stmt in func_def.body:
                self._exec_stmt(stmt)
        except _ReturnSignal as sig:
            self._call_stack.pop()
            return sig.value

        self._call_stack.pop()
        return None

    def _eval_binary_op(self, expr: BinaryOp) -> Any:
        """二項演算"""
        op = expr.op

        # 短絡評価
        if op == "and":
            left = self._eval_expr(expr.left)
            if not left:
                return left
            return self._eval_expr(expr.right)
        if op == "or":
            left = self._eval_expr(expr.left)
            if left:
                return left
            return self._eval_expr(expr.right)

        left = self._eval_expr(expr.left)
        right = self._eval_expr(expr.right)

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise ZeroDivisionError("0で除算することはできません")
            return left / right
        if op == "//":
            if right == 0:
                raise ZeroDivisionError("0で除算することはできません")
            return int(left // right)
        if op == "%":
            return left % right
        if op == "**":
            return left ** right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right
        if op == "&":
            return left & right
        if op == "|":
            return left | right
        raise RuntimeError(f"未対応の演算子です: {op}")

    def _eval_unary_op(self, expr: UnaryOp) -> Any:
        """単項演算"""
        operand = self._eval_expr(expr.operand)
        if expr.op == "not":
            return not operand
        if expr.op == "-":
            return -operand
        if expr.op == "+":
            return +operand
        raise RuntimeError(f"未対応の単項演算子です: {expr.op}")

    def _eval_property_access(self, expr: PropertyAccess) -> Any:
        """プロパティアクセス"""
        obj = self._eval_expr(expr.object)
        prop = expr.property_name
        if prop in ("要素数", "文字数"):
            return len(obj)
        if prop == "行数":
            return obj.rows
        if prop == "列数":
            return obj.cols
        return getattr(obj, prop)

    def _eval_char_at(self, expr: CharAt) -> str:
        """文字アクセス（1-based）"""
        s = self._eval_expr(expr.string)
        idx = self._eval_expr(expr.index)
        return s[idx - 1]

    def _eval_dynamic_array_init(self, expr: DynamicArrayInit) -> Array | Array2D:
        """動的配列初期化"""
        init_val = self._eval_expr(expr.init_value)
        if expr.rows_expr and expr.cols_expr:
            rows = self._eval_expr(expr.rows_expr)
            cols = self._eval_expr(expr.cols_expr)
            return Array2D(rows, cols, init=init_val)
        if expr.size_expr:
            size = self._eval_expr(expr.size_expr)
            return Array(size, init=init_val)
        return Array.from_literal([init_val])


# === ヘルパー関数 ===


def _repr(val: Any) -> str:
    """値の表示用文字列"""
    if val is None:
        return "未定義"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)


def _expr_desc(expr: Expression) -> str:
    """式の簡易説明文字列"""
    if isinstance(expr, Identifier):
        return expr.name
    if isinstance(expr, ArrayAccess):
        arr = _expr_desc(expr.array)
        indices = ", ".join(_expr_desc(i) for i in expr.indices)
        return f"{arr}[{indices}]"
    if isinstance(expr, MemberAccess):
        return f"{_expr_desc(expr.object)}.{expr.member}"
    if isinstance(expr, IntegerLiteral):
        return str(expr.value)
    if isinstance(expr, StringLiteral):
        return f'"{expr.value}"'
    if isinstance(expr, BinaryOp):
        return f"{_expr_desc(expr.left)} {expr.op} {_expr_desc(expr.right)}"
    return type(expr).__name__
