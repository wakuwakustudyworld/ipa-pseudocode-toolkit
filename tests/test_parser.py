"""構文解析器のテスト"""

from ipa_pseudocode.parser.ast_nodes import (
    AppendStatement,
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOp,
    BreakStatement,
    DoWhileStatement,
    ForEachStatement,
    ForStatement,
    FunctionCall,
    Identifier,
    IfStatement,
    IncrementStatement,
    IntegerLiteral,
    MemberAccess,
    PrintStatement,
    ReturnStatement,
    SwapStatement,
    UnaryOp,
    UndefinedLiteral,
    VarDecl,
    WhileStatement,
)
from ipa_pseudocode.parser.grammar import parse


class TestFunctionDef:
    def test_simple_function(self):
        source = """\
○整数型: fee(整数型: age)
  return 0
"""
        prog = parse(source)
        assert len(prog.functions) == 1
        func = prog.functions[0]
        assert func.name == "fee"
        assert func.return_type == "整数型"
        assert len(func.params) == 1
        assert func.params[0].name == "age"
        assert func.params[0].type_annotation == "整数型"

    def test_procedure(self):
        source = """\
○display(整数型: n)
  return
"""
        prog = parse(source)
        func = prog.functions[0]
        assert func.name == "display"
        assert func.return_type is None

    def test_multiple_params(self):
        source = """\
○整数型: add(整数型: a, 整数型: b)
  return a
"""
        prog = parse(source)
        func = prog.functions[0]
        assert len(func.params) == 2
        assert func.params[0].name == "a"
        assert func.params[1].name == "b"


class TestVarDecl:
    def test_simple_decl(self):
        source = """\
○整数型: foo()
  整数型: x
  return x
"""
        prog = parse(source)
        body = prog.functions[0].body
        assert isinstance(body[0], VarDecl)
        assert body[0].type_annotation == "整数型"
        assert body[0].names == ["x"]

    def test_decl_with_init(self):
        source = """\
○整数型: foo()
  整数型: x ← 0
  return x
"""
        prog = parse(source)
        body = prog.functions[0].body
        decl = body[0]
        assert isinstance(decl, VarDecl)
        assert isinstance(decl.initializer, IntegerLiteral)
        assert decl.initializer.value == 0

    def test_multiple_names(self):
        source = """\
○整数型: foo()
  整数型: x, y, z
  return x
"""
        prog = parse(source)
        decl = prog.functions[0].body[0]
        assert isinstance(decl, VarDecl)
        assert decl.names == ["x", "y", "z"]


class TestAssignment:
    def test_simple_assign(self):
        source = """\
○整数型: foo()
  整数型: x
  x ← 42
  return x
"""
        prog = parse(source)
        assign = prog.functions[0].body[1]
        assert isinstance(assign, Assignment)
        assert isinstance(assign.target, Identifier)
        assert assign.target.name == "x"
        assert isinstance(assign.value, IntegerLiteral)
        assert assign.value.value == 42


class TestIfStatement:
    def test_simple_if(self):
        source = """\
○整数型: foo(整数型: x)
  if (x ＝ 1)
    return 10
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert isinstance(if_stmt, IfStatement)
        assert isinstance(if_stmt.condition, BinaryOp)
        assert if_stmt.condition.op == "=="

    def test_if_else(self):
        source = """\
○整数型: foo(整数型: x)
  if (x ＝ 1)
    return 10
  else
    return 20
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert len(if_stmt.else_body) > 0

    def test_if_elseif_else(self):
        source = """\
○整数型: fee(整数型: age)
  整数型: ret
  if (age ≦ 3)
    ret ← 100
  elseif (age ≦ 9)
    ret ← 300
  else
    ret ← 500
  endif
  return ret
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[1]
        assert isinstance(if_stmt, IfStatement)
        assert len(if_stmt.elseif_clauses) == 1
        assert len(if_stmt.else_body) > 0

    def test_japanese_condition_ika(self):
        source = """\
○整数型: foo(整数型: age)
  if (age が 3 以下)
    return 100
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert isinstance(if_stmt.condition, BinaryOp)
        assert if_stmt.condition.op == "<="

    def test_japanese_condition_ijou(self):
        source = """\
○整数型: foo(整数型: n)
  if (n が 10 以上)
    return 1
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert if_stmt.condition.op == ">="

    def test_japanese_condition_undefined(self):
        source = """\
○整数型: foo(整数型: x)
  if (x が 未定義)
    return 0
  endif
  return 1
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert if_stmt.condition.op == "is"
        assert isinstance(if_stmt.condition.right, UndefinedLiteral)

    def test_japanese_condition_undefined_not(self):
        source = """\
○整数型: foo(整数型: x)
  if (x が 未定義でない)
    return 1
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert if_stmt.condition.op == "is not"

    def test_compound_condition_and(self):
        source = """\
○整数型: foo(整数型: x)
  if (x が 1 以上 and x が 10 以下)
    return 1
  endif
  return 0
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert isinstance(if_stmt.condition, BinaryOp)
        assert if_stmt.condition.op == "and"


class TestForStatement:
    def test_increment_for(self):
        source = """\
○整数型: foo()
  整数型: s ← 0
  for (i を 1 から 10 まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
"""
        prog = parse(source)
        for_stmt = prog.functions[0].body[1]
        assert isinstance(for_stmt, ForStatement)
        assert for_stmt.var_name == "i"
        assert for_stmt.direction == "increment"
        assert isinstance(for_stmt.start, IntegerLiteral)
        assert for_stmt.start.value == 1
        assert isinstance(for_stmt.end, IntegerLiteral)
        assert for_stmt.end.value == 10

    def test_decrement_for(self):
        source = """\
○整数型: foo()
  for (i を 10 から 1 まで 1 ずつ減らす)
    return i
  endfor
  return 0
"""
        prog = parse(source)
        for_stmt = prog.functions[0].body[0]
        assert isinstance(for_stmt, ForStatement)
        assert for_stmt.direction == "decrement"

    def test_foreach(self):
        source = """\
○整数型: foo()
  for (item に list の要素を順に代入する)
    return item
  endfor
  return 0
"""
        prog = parse(source)
        for_stmt = prog.functions[0].body[0]
        assert isinstance(for_stmt, ForEachStatement)
        assert for_stmt.var_name == "item"


class TestWhileStatement:
    def test_while(self):
        source = """\
○整数型: foo()
  整数型: i ← 0
  while (i ＜ 10)
    i ← i ＋ 1
  endwhile
  return i
"""
        prog = parse(source)
        while_stmt = prog.functions[0].body[1]
        assert isinstance(while_stmt, WhileStatement)
        assert isinstance(while_stmt.condition, BinaryOp)
        assert while_stmt.condition.op == "<"


class TestDoWhileStatement:
    def test_do_while(self):
        source = """\
○整数型: foo()
  整数型: i ← 0
  do
    i ← i ＋ 1
  while (i ＜ 10)
  return i
"""
        prog = parse(source)
        do_stmt = prog.functions[0].body[1]
        assert isinstance(do_stmt, DoWhileStatement)
        assert isinstance(do_stmt.condition, BinaryOp)
        assert do_stmt.condition.op == "<"


class TestReturnStatement:
    def test_return_value(self):
        source = """\
○整数型: foo()
  return 42
"""
        prog = parse(source)
        ret = prog.functions[0].body[0]
        assert isinstance(ret, ReturnStatement)
        assert isinstance(ret.value, IntegerLiteral)
        assert ret.value.value == 42

    def test_return_void(self):
        source = """\
○display()
  return
"""
        prog = parse(source)
        ret = prog.functions[0].body[0]
        assert isinstance(ret, ReturnStatement)
        assert ret.value is None


class TestJapaneseActions:
    def test_append(self):
        source = """\
○foo()
  pnListの末尾にiの値を追加する
"""
        prog = parse(source)
        stmt = prog.functions[0].body[0]
        assert isinstance(stmt, AppendStatement)

    def test_swap(self):
        source = """\
○foo()
  data[i]とdata[j]の値を入れ替える
"""
        prog = parse(source)
        stmt = prog.functions[0].body[0]
        assert isinstance(stmt, SwapStatement)

    def test_increment(self):
        source = """\
○foo()
  countの値を1増やす
"""
        prog = parse(source)
        stmt = prog.functions[0].body[0]
        assert isinstance(stmt, IncrementStatement)

    def test_break(self):
        source = """\
○foo()
  while (true)
    繰返し処理を終了する
  endwhile
"""
        prog = parse(source)
        body = prog.functions[0].body[0].body
        assert isinstance(body[0], BreakStatement)

    def test_print(self):
        source = """\
○foo()
  "hello"を出力する
"""
        prog = parse(source)
        stmt = prog.functions[0].body[0]
        assert isinstance(stmt, PrintStatement)


class TestExpressions:
    def test_binary_op(self):
        source = """\
○整数型: foo()
  return 1 ＋ 2
"""
        prog = parse(source)
        ret = prog.functions[0].body[0]
        assert isinstance(ret.value, BinaryOp)
        assert ret.value.op == "+"

    def test_array_access(self):
        source = """\
○整数型: foo()
  整数型の配列: arr
  return arr[1]
"""
        prog = parse(source)
        ret = prog.functions[0].body[1]
        assert isinstance(ret.value, ArrayAccess)

    def test_function_call(self):
        source = """\
○整数型: foo()
  return bar(1, 2)
"""
        prog = parse(source)
        ret = prog.functions[0].body[0]
        assert isinstance(ret.value, FunctionCall)
        assert len(ret.value.arguments) == 2

    def test_member_access(self):
        source = """\
○整数型: foo()
  return obj.field
"""
        prog = parse(source)
        ret = prog.functions[0].body[0]
        assert isinstance(ret.value, MemberAccess)
        assert ret.value.member == "field"

    def test_array_literal(self):
        source = """\
○整数型: foo()
  整数型の配列: arr ← {1, 2, 3}
  return arr[1]
"""
        prog = parse(source)
        decl = prog.functions[0].body[0]
        assert isinstance(decl.initializer, ArrayLiteral)
        assert len(decl.initializer.elements) == 3

    def test_unary_not(self):
        source = """\
○整数型: foo()
  if (not true)
    return 0
  endif
  return 1
"""
        prog = parse(source)
        if_stmt = prog.functions[0].body[0]
        assert isinstance(if_stmt.condition, UnaryOp)
        assert if_stmt.condition.op == "not"


class TestGlobalVars:
    def test_global_decl(self):
        source = """\
大域: 整数型: gCount ← 0
○整数型: foo()
  return gCount
"""
        prog = parse(source)
        assert len(prog.globals) == 1
        g = prog.globals[0]
        assert isinstance(g, VarDecl)
        assert g.is_global
        assert g.names == ["gCount"]
