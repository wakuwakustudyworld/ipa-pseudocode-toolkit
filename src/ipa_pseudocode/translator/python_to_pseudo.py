"""Python→擬似言語変換器

Python の ast モジュールでパースした AST を走査し、IPA 擬似言語コードを生成する。
"""

from __future__ import annotations

import ast
from typing import Any


def reverse_translate(source: str) -> str:
    """PythonソースコードをIPA擬似言語に変換する

    Args:
        source: Pythonソースコード

    Returns:
        IPA擬似言語コード文字列
    """
    translator = PythonToPseudoTranslator()
    return translator.translate(source)


# === Python→擬似言語 演算子マッピング ===

_PY_TO_PSEUDO_BINOP: dict[type, str] = {
    ast.Add: "＋",
    ast.Sub: "−",
    ast.Mult: "×",
    ast.Div: "÷",
    ast.FloorDiv: "÷",  # 後処理で「の商」を付与
    ast.Mod: "mod",
    ast.Pow: "**",
    ast.BitAnd: "∧",
    ast.BitOr: "∨",
}

_PY_TO_PSEUDO_CMPOP: dict[type, str] = {
    ast.Eq: "＝",
    ast.NotEq: "≠",
    ast.Lt: "＜",
    ast.Gt: "＞",
    ast.LtE: "≦",
    ast.GtE: "≧",
    ast.Is: "＝",
    ast.IsNot: "≠",
}

_PY_TO_PSEUDO_BOOLOP: dict[type, str] = {
    ast.And: "and",
    ast.Or: "or",
}

_PY_TO_PSEUDO_UNARYOP: dict[type, str] = {
    ast.Not: "not",
    ast.USub: "−",
    ast.UAdd: "＋",
}

# Python型ヒント → 擬似言語型名
_PY_TYPE_TO_PSEUDO: dict[str, str] = {
    "int": "整数型",
    "float": "実数型",
    "str": "文字列型",
    "bool": "論理型",
    "Array": "整数型の配列",
    "Array2D": "整数型の二次元配列",
    "list": "整数型の配列",
    "None": "",
}

# 演算子の優先順位（括弧が必要かの判定用）
_OP_PREC: dict[str, int] = {
    "or": 1,
    "and": 2,
    "＝": 4, "≠": 4, "＜": 4, "＞": 4, "≦": 4, "≧": 4,
    "∨": 5,
    "∧": 6,
    "＋": 8, "−": 8,
    "×": 9, "÷": 9, "mod": 9,
    "**": 10,
}


class PythonToPseudoTranslator:
    """Python AST → 擬似言語テキスト変換器"""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._indent_level: int = 0
        self._indent_str: str = "  "  # 擬似言語は全角スペースor半角2スペース
        self._global_names: set[str] = set()

    def translate(self, source: str) -> str:
        """PythonソースコードをIPA擬似言語に変換する"""
        tree = ast.parse(source)

        # 事前パス: global変数を収集
        self._collect_globals(tree)

        # import文をスキップしてトップレベル文を処理
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            self._translate_node(node, is_toplevel=True)

        result = "\n".join(self._lines)
        # 末尾改行を整理
        result = result.rstrip("\n") + "\n"
        return result

    def _collect_globals(self, tree: ast.Module) -> None:
        """グローバル変数名を収集する（関数外の代入から推定）"""
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self._global_names.add(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                self._global_names.add(node.target.id)

    # === 出力ヘルパー ===

    def _add_line(self, line: str) -> None:
        self._lines.append(f"{self._indent_str * self._indent_level}{line}")

    def _indent(self) -> None:
        self._indent_level += 1

    def _dedent(self) -> None:
        self._indent_level = max(0, self._indent_level - 1)

    # === ノード変換ディスパッチ ===

    def _translate_node(self, node: ast.AST, is_toplevel: bool = False) -> None:
        if isinstance(node, ast.FunctionDef):
            self._translate_function_def(node)
        elif isinstance(node, ast.Assign):
            self._translate_assign(node, is_toplevel=is_toplevel)
        elif isinstance(node, ast.AnnAssign):
            self._translate_ann_assign(node, is_toplevel=is_toplevel)
        elif isinstance(node, ast.AugAssign):
            self._translate_aug_assign(node)
        elif isinstance(node, ast.If):
            self._translate_if(node)
        elif isinstance(node, ast.While):
            self._translate_while(node)
        elif isinstance(node, ast.For):
            self._translate_for(node)
        elif isinstance(node, ast.Return):
            self._translate_return(node)
        elif isinstance(node, ast.Break):
            self._add_line("繰返し処理を終了する")
        elif isinstance(node, ast.Continue):
            self._add_line("繰返し処理の先頭に戻る")
        elif isinstance(node, ast.Expr):
            self._translate_expr_stmt(node)
        elif isinstance(node, ast.Global):
            pass  # global宣言は擬似言語では不要（大域宣言で処理済み）
        elif isinstance(node, ast.Pass):
            pass  # passは擬似言語では不要

    # === 関数定義 ===

    def _translate_function_def(self, node: ast.FunctionDef) -> None:
        # 戻り値の型
        return_type = ""
        if node.returns:
            return_type = self._python_type_to_pseudo(node.returns)

        # 仮引数
        params: list[str] = []
        for arg in node.args.args:
            param_name = self._restore_safe_name(arg.arg)
            param_type = ""
            if arg.annotation:
                param_type = self._python_type_to_pseudo(arg.annotation)
            if param_type:
                params.append(f"{param_type}: {param_name}")
            else:
                params.append(param_name)

        params_str = ", ".join(params)
        if return_type:
            self._add_line(f"○{return_type}: {node.name}({params_str})")
        else:
            self._add_line(f"○{node.name}({params_str})")

        self._indent()
        for stmt in node.body:
            self._translate_node(stmt)
        self._dedent()

    # === 代入文 ===

    def _translate_assign(self, node: ast.Assign, is_toplevel: bool = False) -> None:
        # swap パターン: a, b = b, a
        if self._is_swap(node):
            target_tuple = node.targets[0]
            left_str = self._expr(target_tuple.elts[0])  # type: ignore[attr-defined]
            right_str = self._expr(target_tuple.elts[1])  # type: ignore[attr-defined]
            self._add_line(f"{left_str}と{right_str}の値を入れ替える")
            return

        target = node.targets[0]
        value = self._expr(node.value)
        target_str = self._expr(target)

        if is_toplevel and isinstance(target, ast.Name) and target.id in self._global_names:
            # 関数内で使われるグローバル変数の場合は大域宣言
            has_global_ref = self._has_global_reference(target.id)
            if has_global_ref:
                self._add_line(f"大域: {target_str} ← {value}")
                return

        self._add_line(f"{target_str} ← {value}")

    def _translate_ann_assign(self, node: ast.AnnAssign, is_toplevel: bool = False) -> None:
        """型ヒント付き代入: x: int = 5"""
        type_str = self._python_type_to_pseudo(node.annotation)
        target_str = self._expr(node.target)

        prefix = ""
        if is_toplevel and isinstance(node.target, ast.Name) and node.target.id in self._global_names:
            if self._has_global_reference(node.target.id):
                prefix = "大域: "

        if node.value is not None:
            value_str = self._expr(node.value)
            if type_str:
                self._add_line(f"{prefix}{type_str}: {target_str} ← {value_str}")
            else:
                self._add_line(f"{prefix}{target_str} ← {value_str}")
        else:
            if type_str:
                self._add_line(f"{prefix}{type_str}: {target_str}")
            else:
                self._add_line(f"{prefix}{target_str}")

    def _translate_aug_assign(self, node: ast.AugAssign) -> None:
        """+=, -= 等"""
        target_str = self._expr(node.target)
        value_str = self._expr(node.value)
        if isinstance(node.op, ast.Add):
            self._add_line(f"{target_str}の値を{value_str}増やす")
        elif isinstance(node.op, ast.Sub):
            self._add_line(f"{target_str}の値を{value_str}減らす")
        else:
            # その他の複合代入は普通の代入に展開
            op = _PY_TO_PSEUDO_BINOP.get(type(node.op), "?")
            self._add_line(f"{target_str} ← {target_str} {op} {value_str}")

    # === 制御フロー ===

    def _translate_if(self, node: ast.If, is_elseif: bool = False) -> None:
        cond = self._expr(node.test)
        keyword = "elseif" if is_elseif else "if"
        self._add_line(f"{keyword} ({cond})")

        self._indent()
        for stmt in node.body:
            self._translate_node(stmt)
        self._dedent()

        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # elif チェーン
                self._translate_if(node.orelse[0], is_elseif=True)
            else:
                self._add_line("else")
                self._indent()
                for stmt in node.orelse:
                    self._translate_node(stmt)
                self._dedent()

        # 最外側の if のみ endif を出力（elseif チェーンの末端でも出力）
        if not is_elseif:
            self._add_line("endif")

    def _translate_while(self, node: ast.While) -> None:
        # do-while パターン検出: while True: ... if not cond: break
        do_while_cond = self._detect_do_while(node)
        if do_while_cond is not None:
            self._add_line("do")
            self._indent()
            # 最後のif文（do-while終了条件）以外の文を出力
            for stmt in node.body[:-1]:
                self._translate_node(stmt)
            self._dedent()
            self._add_line(f"while ({self._expr(do_while_cond)})")
            return

        cond = self._expr(node.test)
        self._add_line(f"while ({cond})")
        self._indent()
        for stmt in node.body:
            self._translate_node(stmt)
        self._dedent()
        self._add_line("endwhile")

    def _translate_for(self, node: ast.For) -> None:
        # for x in range(...) パターン
        range_info = self._detect_range_for(node)
        if range_info:
            var, start, end, step, direction = range_info
            if direction == "increment":
                self._add_line(
                    f"for ({var} を {start} から {end} まで {step} ずつ増やす)"
                )
            else:
                self._add_line(
                    f"for ({var} を {start} から {end} まで {step} ずつ減らす)"
                )
        else:
            # for-each
            var = self._expr(node.target)
            iterable = self._expr(node.iter)
            self._add_line(
                f"for ({var} に {iterable} の要素を順に代入する)"
            )

        self._indent()
        for stmt in node.body:
            self._translate_node(stmt)
        self._dedent()
        self._add_line("endfor")

    def _translate_return(self, node: ast.Return) -> None:
        if node.value is not None:
            self._add_line(f"return {self._expr(node.value)}")
        else:
            self._add_line("return")

    def _translate_expr_stmt(self, node: ast.Expr) -> None:
        """式文（関数呼び出し等）"""
        call = node.value
        if isinstance(call, ast.Call):
            # print() → 出力
            if isinstance(call.func, ast.Name) and call.func.id == "print":
                self._translate_print_call(call)
                return
            # obj.append(val) → 末尾追加
            if isinstance(call.func, ast.Attribute) and call.func.attr == "append":
                obj = self._expr(call.func.value)
                val = self._expr(call.args[0]) if call.args else ""
                self._add_line(f"{obj}の末尾に{val}の値を追加する")
                return

        self._add_line(self._expr(node.value))

    def _translate_print_call(self, call: ast.Call) -> None:
        """print関数の呼び出しを擬似言語の出力文に変換"""
        args = [self._expr(a) for a in call.args]

        # sep= キーワード引数を検出
        sep = ""
        for kw in call.keywords:
            if kw.arg == "sep":
                if isinstance(kw.value, ast.Constant):
                    if kw.value.value == ",":
                        sep = "コンマ"
                    elif kw.value.value == " ":
                        sep = "空白"
                    else:
                        sep = kw.value.value

        values_str = "の値と".join(args) + "の値"
        if sep:
            self._add_line(f"{values_str}をこの順に{sep}区切りで出力する")
        elif len(args) == 1:
            self._add_line(f"{args[0]}を出力する")
        else:
            self._add_line(f"{values_str}をこの順に出力する")

    # === 式の変換 ===

    def _expr(self, node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            return self._constant(node)
        if isinstance(node, ast.Name):
            return self._name(node)
        if isinstance(node, ast.BinOp):
            return self._binop(node)
        if isinstance(node, ast.UnaryOp):
            return self._unaryop(node)
        if isinstance(node, ast.BoolOp):
            return self._boolop(node)
        if isinstance(node, ast.Compare):
            return self._compare(node)
        if isinstance(node, ast.Call):
            return self._call(node)
        if isinstance(node, ast.Subscript):
            return self._subscript(node)
        if isinstance(node, ast.Attribute):
            return self._attribute(node)
        if isinstance(node, ast.Tuple):
            return ", ".join(self._expr(e) for e in node.elts)
        if isinstance(node, ast.List):
            elements = ", ".join(self._expr(e) for e in node.elts)
            return "{" + elements + "}"
        if isinstance(node, ast.IfExp):
            # Python三項演算子 → if文に変換は文レベルで処理すべきだが、
            # 式として出現する場合はそのまま表現
            cond = self._expr(node.test)
            body = self._expr(node.body)
            orelse = self._expr(node.orelse)
            return f"({body} if {cond} else {orelse})"
        # フォールバック
        return ast.dump(node)

    def _constant(self, node: ast.Constant) -> str:
        if node.value is None:
            return "未定義"
        if node.value is True:
            return "true"
        if node.value is False:
            return "false"
        if isinstance(node.value, str):
            return f'"{node.value}"'
        if isinstance(node.value, float) and node.value == float("-inf"):
            return "−∞"
        return str(node.value)

    _PYTHON_KEYWORDS = frozenset({
        "in", "is", "not", "and", "or", "for", "if", "else", "while", "return",
        "break", "class", "def", "from", "import", "pass", "with", "as",
        "try", "except", "finally", "raise", "del", "global", "lambda", "yield",
        "assert", "elif", "nonlocal", "continue",
    })

    @classmethod
    def _restore_safe_name(cls, name: str) -> str:
        """Python予約語の _ 末尾を除去する（pseudo_to_python が付けたもの）"""
        if name.endswith("_") and name[:-1] in cls._PYTHON_KEYWORDS:
            return name[:-1]
        return name

    def _name(self, node: ast.Name) -> str:
        name = self._restore_safe_name(node.id)
        if name == "None":
            return "未定義"
        if name == "True":
            return "true"
        if name == "False":
            return "false"
        return name

    def _binop(self, node: ast.BinOp) -> str:
        left = self._expr(node.left)
        right = self._expr(node.right)
        op_type = type(node.op)
        op_str = _PY_TO_PSEUDO_BINOP.get(op_type, "?")

        # 整数除算: a // b → a ÷ bの商
        if isinstance(node.op, ast.FloorDiv):
            left = self._parenthesize_binop(node.left, left, "÷", is_right=False)
            right = self._parenthesize_binop(node.right, right, "÷", is_right=True)
            return f"{left} ÷ {right}の商"

        # べき乗: x ** 2 → xの2乗, x ** 0.5 → xの正の平方根
        if isinstance(node.op, ast.Pow):
            if isinstance(node.right, ast.Constant):
                if node.right.value == 2:
                    return f"{left}の2乗"
                if node.right.value == 0.5:
                    return f"{left}の正の平方根"

        left = self._parenthesize_binop(node.left, left, op_str, is_right=False)
        right = self._parenthesize_binop(node.right, right, op_str, is_right=True)
        return f"{left} {op_str} {right}"

    def _parenthesize_binop(self, child: ast.AST, child_str: str,
                            parent_op: str, is_right: bool) -> str:
        """必要に応じて子式に括弧を付ける"""
        if not isinstance(child, ast.BinOp):
            return child_str
        child_op = _PY_TO_PSEUDO_BINOP.get(type(child.op), "?")
        child_prec = _OP_PREC.get(child_op, 99)
        parent_prec = _OP_PREC.get(parent_op, 99)
        if child_prec < parent_prec or (child_prec == parent_prec and is_right):
            return f"({child_str})"
        return child_str

    def _unaryop(self, node: ast.UnaryOp) -> str:
        operand = self._expr(node.operand)
        op_str = _PY_TO_PSEUDO_UNARYOP.get(type(node.op), "?")
        if isinstance(node.op, ast.Not):
            return f"not {operand}"
        return f"{op_str}{operand}"

    def _boolop(self, node: ast.BoolOp) -> str:
        op_str = _PY_TO_PSEUDO_BOOLOP.get(type(node.op), "?")
        parts = [self._expr(v) for v in node.values]
        return f" {op_str} ".join(parts)

    def _compare(self, node: ast.Compare) -> str:
        parts = [self._expr(node.left)]
        for op, comparator in zip(node.ops, node.comparators):
            op_str = _PY_TO_PSEUDO_CMPOP.get(type(op), "?")
            # is None → ＝ 未定義
            if isinstance(op, ast.Is) and isinstance(comparator, ast.Constant) and comparator.value is None:
                parts.append("＝")
                parts.append("未定義")
            elif isinstance(op, ast.IsNot) and isinstance(comparator, ast.Constant) and comparator.value is None:
                parts.append("≠")
                parts.append("未定義")
            else:
                parts.append(op_str)
                parts.append(self._expr(comparator))
        return " ".join(parts)

    def _call(self, node: ast.Call) -> str:
        # len(x) → xの要素数
        if isinstance(node.func, ast.Name) and node.func.id == "len" and len(node.args) == 1:
            return f"{self._expr(node.args[0])}の要素数"

        # int(x ** 0.5) → xの正の平方根の整数部分
        if isinstance(node.func, ast.Name) and node.func.id == "int" and len(node.args) == 1:
            inner = node.args[0]
            if isinstance(inner, ast.BinOp) and isinstance(inner.op, ast.Pow):
                if isinstance(inner.right, ast.Constant) and inner.right.value == 0.5:
                    return f"{self._expr(inner.left)}の正の平方根の整数部分"

        # 通常の関数呼び出し
        func_str = self._expr(node.func)
        args = ", ".join(self._expr(a) for a in node.args)
        return f"{func_str}({args})"

    def _subscript(self, node: ast.Subscript) -> str:
        obj = self._expr(node.value)
        if isinstance(node.slice, ast.Tuple):
            indices = ", ".join(self._expr(e) for e in node.slice.elts)
            return f"{obj}[{indices}]"
        idx = self._expr(node.slice)
        return f"{obj}[{idx}]"

    def _attribute(self, node: ast.Attribute) -> str:
        obj = self._expr(node.value)
        attr = node.attr
        # .rows → の行数, .cols → の列数
        if attr == "rows":
            return f"{obj}の行数"
        if attr == "cols":
            return f"{obj}の列数"
        return f"{obj}.{attr}"

    # === パターン検出 ===

    def _is_swap(self, node: ast.Assign) -> bool:
        """a, b = b, a パターンかどうか"""
        if len(node.targets) != 1:
            return False
        target = node.targets[0]
        value = node.value
        if not isinstance(target, ast.Tuple) or not isinstance(value, ast.Tuple):
            return False
        if len(target.elts) != 2 or len(value.elts) != 2:
            return False
        # ターゲットとバリューが逆順か（式の文字列表現で比較、ctx の違いを無視）
        t0 = self._expr(target.elts[0])
        t1 = self._expr(target.elts[1])
        v0 = self._expr(value.elts[0])
        v1 = self._expr(value.elts[1])
        return t0 == v1 and t1 == v0

    def _detect_do_while(self, node: ast.While) -> ast.AST | None:
        """while True: ... if not cond: break パターンを検出"""
        # while True か
        if not (isinstance(node.test, ast.Constant) and node.test.value is True):
            return None
        if not node.body:
            return None
        # 最後の文が if not cond: break か
        last = node.body[-1]
        if not isinstance(last, ast.If):
            return None
        if len(last.body) != 1 or not isinstance(last.body[0], ast.Break):
            return None
        if last.orelse:
            return None
        # 条件を取得（not を剥がす）
        test = last.test
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return test.operand
        # not (...) の括弧パターン
        return None

    def _detect_range_for(self, node: ast.For) -> tuple[str, str, str, str, str] | None:
        """for x in range(...) パターンを検出して (var, start, end, step, direction) を返す"""
        if not isinstance(node.target, ast.Name):
            return None
        if not isinstance(node.iter, ast.Call):
            return None
        if not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
            return None

        var = node.target.id
        args = node.iter.args

        if len(args) == 1:
            # range(n) → 0 から n-1 まで
            end_expr = args[0]
            end = self._simplify_range_bound(end_expr, subtract=1)
            return (var, "0", end, "1", "increment")

        if len(args) >= 2:
            start = self._expr(args[0])
            end_expr = args[1]
            step_val = 1
            direction = "increment"

            if len(args) >= 3:
                step_node = args[2]
                # 負のステップ: range(n, m, -1) → decrement
                if isinstance(step_node, ast.UnaryOp) and isinstance(step_node.op, ast.USub):
                    if isinstance(step_node.operand, ast.Constant):
                        step_val = step_node.operand.value
                        direction = "decrement"
                elif isinstance(step_node, ast.Constant):
                    if step_node.value < 0:
                        step_val = abs(step_node.value)
                        direction = "decrement"
                    else:
                        step_val = step_node.value

            if direction == "increment":
                # range(start, end + 1) → start から end まで
                end = self._simplify_range_bound(end_expr, subtract=1)
            else:
                # range(start, end - 1, -step) → start から end まで (decrement)
                end = self._simplify_range_bound(end_expr, add=1)

            return (var, start, end, str(step_val), direction)

        return None

    def _simplify_range_bound(self, node: ast.AST, subtract: int = 0, add: int = 0) -> str:
        """range の境界値を簡約化する

        range(start, end + 1) の end + 1 を end に、
        range(start, end - 1, -1) の end - 1 を end に変換する。
        """
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Add) and isinstance(node.right, ast.Constant):
                if subtract and node.right.value == subtract:
                    return self._expr(node.left)
            if isinstance(node.op, ast.Sub) and isinstance(node.right, ast.Constant):
                if add and node.right.value == add:
                    return self._expr(node.left)
        # 簡約化できない場合はそのまま
        expr = self._expr(node)
        if subtract:
            return f"{expr} − {subtract}"
        if add:
            return f"{expr} ＋ {add}"
        return expr

    # === 型変換 ===

    def _python_type_to_pseudo(self, node: ast.AST) -> str:
        """Python型ヒントAST → 擬似言語型名"""
        if isinstance(node, ast.Constant) and node.value is None:
            return ""
        if isinstance(node, ast.Name):
            return _PY_TYPE_TO_PSEUDO.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            return _PY_TYPE_TO_PSEUDO.get(node.attr, node.attr)
        if isinstance(node, ast.Subscript):
            # list[int] など
            if isinstance(node.value, ast.Name) and node.value.id == "list":
                inner = self._python_type_to_pseudo(node.slice)
                return f"{inner}の配列"
        return ""

    # === ヘルパー ===

    def _has_global_reference(self, name: str) -> bool:
        """ASTのどこかの関数内でglobal宣言されているか"""
        # _collect_globals で収集済みのグローバル変数が関数内で参照されているか
        # ここでは簡易実装として常に True（トップレベル代入は大域として扱う方が安全）
        return True
