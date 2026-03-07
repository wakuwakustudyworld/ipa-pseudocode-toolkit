"""Python→擬似言語 逆変換テスト"""

import ipa_pseudocode


class TestBasicStatements:
    """基本的な文の変換"""

    def test_assignment(self):
        result = ipa_pseudocode.reverse_translate("x = 42\n")
        assert "x ← 42" in result

    def test_annotated_assignment(self):
        result = ipa_pseudocode.reverse_translate("x: int = 42\n")
        assert "整数型: x ← 42" in result

    def test_none_to_undefined(self):
        result = ipa_pseudocode.reverse_translate("x = None\n")
        assert "未定義" in result

    def test_bool_literals(self):
        result = ipa_pseudocode.reverse_translate("x = True\ny = False\n")
        assert "true" in result
        assert "false" in result


class TestArithmeticOperators:
    """演算子の変換"""

    def test_addition(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 3 + 4
""")
        assert "3 ＋ 4" in result

    def test_subtraction(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 10 - 3
""")
        assert "10 − 3" in result

    def test_multiplication(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 6 * 7
""")
        assert "6 × 7" in result

    def test_division(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 10 / 3
""")
        assert "10 ÷ 3" in result

    def test_integer_division(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 10 // 3
""")
        assert "10 ÷ 3の商" in result

    def test_modulo(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 10 % 3
""")
        assert "10 mod 3" in result

    def test_comparison(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(a, b):
    return a == b
""")
        assert "a ＝ b" in result

    def test_not_equal(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(a, b):
    return a != b
""")
        assert "a ≠ b" in result

    def test_less_equal(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(a, b):
    return a <= b
""")
        assert "a ≦ b" in result

    def test_greater_equal(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(a, b):
    return a >= b
""")
        assert "a ≧ b" in result


class TestControlFlow:
    """制御フローの変換"""

    def test_if_else_endif(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(x):
    if x > 0:
        return 1
    else:
        return 0
""")
        assert "if" in result
        assert "else" in result
        assert "endif" in result

    def test_elif(self):
        result = ipa_pseudocode.reverse_translate("""\
def fee(age):
    if age <= 3:
        ret = 100
    elif age <= 9:
        ret = 300
    else:
        ret = 500
    return ret
""")
        assert "elseif" in result
        assert "endif" in result

    def test_while_loop(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    i = 0
    while i < 5:
        i = i + 1
""")
        assert "while" in result
        assert "endwhile" in result

    def test_do_while(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    i = 0
    while True:
        i = i + 1
        if not (i < 5):
            break
""")
        assert "do" in result
        assert "while (i ＜ 5)" in result
        # endwhile は出ない（do-while構文）
        assert "endwhile" not in result

    def test_for_increment(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    s = 0
    for i in range(1, 10 + 1):
        s = s + i
""")
        assert "for" in result
        assert "増やす" in result
        assert "endfor" in result

    def test_for_decrement(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    for i in range(10, 1 - 1, -1):
        pass
""")
        assert "減らす" in result

    def test_for_each(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(arr):
    for x in arr:
        pass
""")
        assert "の要素を順に代入する" in result

    def test_break(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    while True:
        break
""")
        assert "繰返し処理を終了する" in result

    def test_return(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    return 42
""")
        assert "return 42" in result


class TestFunctionDef:
    """関数定義の変換"""

    def test_simple_function(self):
        result = ipa_pseudocode.reverse_translate("""\
def add(a, b):
    return a + b
""")
        assert "○add(a, b)" in result

    def test_typed_function(self):
        result = ipa_pseudocode.reverse_translate("""\
def add(a: int, b: int) -> int:
    return a + b
""")
        assert "○整数型: add(整数型: a, 整数型: b)" in result

    def test_no_return_type(self):
        result = ipa_pseudocode.reverse_translate("""\
def greet(name: str):
    pass
""")
        assert "○greet(文字列型: name)" in result


class TestSpecialPatterns:
    """特殊パターンの変換"""

    def test_swap(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    a, b = b, a
""")
        assert "aとbの値を入れ替える" in result

    def test_append(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(arr, val):
    arr.append(val)
""")
        assert "arrの末尾にvalの値を追加する" in result

    def test_augmented_add(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    count += 1
""")
        assert "countの値を1増やす" in result

    def test_augmented_sub(self):
        result = ipa_pseudocode.reverse_translate("""\
def f():
    count -= 1
""")
        assert "countの値を1減らす" in result

    def test_print_simple(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(x):
    print(x)
""")
        assert "xを出力する" in result

    def test_print_separator(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(x, y):
    print(x, y, sep=",")
""")
        assert "コンマ区切り" in result
        assert "出力する" in result

    def test_len_to_property(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(arr):
    return len(arr)
""")
        assert "arrの要素数" in result

    def test_square(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(n):
    return n ** 2
""")
        assert "nの2乗" in result

    def test_sqrt(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(x):
    return x ** 0.5
""")
        assert "xの正の平方根" in result

    def test_sqrt_int_part(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(n):
    return int(n ** 0.5)
""")
        assert "nの正の平方根の整数部分" in result

    def test_is_none(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(x):
    if x is None:
        return True
""")
        assert "＝ 未定義" in result

    def test_rows_cols(self):
        result = ipa_pseudocode.reverse_translate("""\
def f(mat):
    return mat.rows
""")
        assert "matの行数" in result

    def test_safe_name_restore(self):
        """Python予約語の _ 末尾が除去される"""
        result = ipa_pseudocode.reverse_translate("""\
def f(in_):
    return in_
""")
        assert "in" in result
        assert "in_" not in result


class TestRoundTrip:
    """擬似言語→Python→擬似言語 の往復変換テスト"""

    def test_simple_function_roundtrip(self):
        """変換結果が意味的に等価であることを確認"""
        pseudo_source = """\
○整数型: add(整数型: a, 整数型: b)
  return a ＋ b
"""
        # 擬似言語 → Python
        python_code = ipa_pseudocode.translate(pseudo_source)
        # Python → 擬似言語
        result = ipa_pseudocode.reverse_translate(python_code)

        assert "add" in result
        assert "＋" in result
        assert "return" in result

    def test_for_loop_roundtrip(self):
        pseudo_source = """\
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
"""
        python_code = ipa_pseudocode.translate(pseudo_source)
        result = ipa_pseudocode.reverse_translate(python_code)

        assert "for" in result
        assert "増やす" in result
        assert "endfor" in result
        assert "return" in result

    def test_if_elseif_roundtrip(self):
        pseudo_source = """\
○整数型: fee(整数型: age)
  整数型: ret
  if (age が 3 以下)
    ret ← 100
  elseif (age が 9 以下)
    ret ← 300
  else
    ret ← 500
  endif
  return ret
"""
        python_code = ipa_pseudocode.translate(pseudo_source)
        result = ipa_pseudocode.reverse_translate(python_code)

        assert "if" in result
        assert "elseif" in result
        assert "else" in result
        assert "endif" in result

    def test_while_roundtrip(self):
        pseudo_source = """\
○整数型: countUp(整数型: limit)
  整数型: i ← 0
  while (i ＜ limit)
    i ← i ＋ 1
  endwhile
  return i
"""
        python_code = ipa_pseudocode.translate(pseudo_source)
        result = ipa_pseudocode.reverse_translate(python_code)

        assert "while" in result
        assert "endwhile" in result

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
        # 元の擬似言語を実行
        original_result = ipa_pseudocode.call_function(pseudo_source, "total", 10)

        # 擬似言語 → Python → 擬似言語 と往復
        python_code = ipa_pseudocode.translate(pseudo_source)
        reversed_pseudo = ipa_pseudocode.reverse_translate(python_code)

        # 往復後の擬似言語を実行
        roundtrip_result = ipa_pseudocode.call_function(reversed_pseudo, "total", 10)

        assert original_result == roundtrip_result == 55


class TestImportSkip:
    """import文がスキップされること"""

    def test_import_skipped(self):
        result = ipa_pseudocode.reverse_translate("""\
from ipa_pseudocode.core.array import Array

def f():
    return 1
""")
        assert "import" not in result
        assert "○f()" in result


class TestVersion:
    """バージョン"""

    def test_version(self):
        assert ipa_pseudocode.__version__ == "0.3.0"
