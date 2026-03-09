"""変換器のテスト"""

from ipa_pseudocode.parser.grammar import parse
from ipa_pseudocode.translator.pseudo_to_python import translate


def _translate(source: str) -> str:
    """擬似言語→Pythonコード変換ヘルパー"""
    prog = parse(source)
    return translate(prog)


class TestFunctionTranslation:
    def test_simple_function(self):
        code = _translate("""\
○整数型: foo()
  return 42
""")
        assert "def foo():" in code
        assert "return 42" in code

    def test_function_with_params(self):
        code = _translate("""\
○整数型: add(整数型: a, 整数型: b)
  return a ＋ b
""")
        assert "def add(a, b):" in code
        assert "return a + b" in code

    def test_procedure(self):
        code = _translate("""\
○display(整数型: n)
  return
""")
        assert "def display(n):" in code
        assert "return" in code


class TestVarDeclTranslation:
    def test_simple_decl(self):
        code = _translate("""\
○整数型: foo()
  整数型: x
  return x
""")
        assert "x = None" in code

    def test_decl_with_init(self):
        code = _translate("""\
○整数型: foo()
  整数型: x ← 0
  return x
""")
        assert "x = 0" in code


class TestAssignmentTranslation:
    def test_simple_assign(self):
        code = _translate("""\
○整数型: foo()
  整数型: x
  x ← 42
  return x
""")
        assert "x = 42" in code


class TestIfTranslation:
    def test_if_elseif_else(self):
        code = _translate("""\
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
""")
        assert "if age <= 3:" in code
        assert "elif age <= 9:" in code
        assert "else:" in code
        assert "ret = 100" in code
        assert "ret = 300" in code
        assert "ret = 500" in code


class TestForTranslation:
    def test_increment_for(self):
        code = _translate("""\
○整数型: foo()
  整数型: s ← 0
  for (i を 1 から 10 まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
""")
        assert "for i in range(1, 10 + 1):" in code

    def test_decrement_for(self):
        code = _translate("""\
○整数型: foo()
  for (i を 10 から 1 まで 1 ずつ減らす)
    return i
  endfor
  return 0
""")
        assert "for i in range(10, 1 - 1, -1):" in code

    def test_for_with_step(self):
        code = _translate("""\
○整数型: foo()
  for (i を 0 から 10 まで 2 ずつ増やす)
    return i
  endfor
  return 0
""")
        assert "for i in range(0, 10 + 1, 2):" in code

    def test_foreach(self):
        code = _translate("""\
○foo()
  for (item に items の要素を順に代入する)
    return
  endfor
""")
        assert "for item in items:" in code


class TestWhileTranslation:
    def test_while(self):
        code = _translate("""\
○整数型: foo()
  整数型: i ← 0
  while (i ＜ 10)
    i ← i ＋ 1
  endwhile
  return i
""")
        assert "while i < 10:" in code


class TestDoWhileTranslation:
    def test_do_while(self):
        code = _translate("""\
○整数型: foo()
  整数型: i ← 0
  do
    i ← i ＋ 1
  while (i ＜ 10)
  return i
""")
        assert "while True:" in code
        assert "if not (i < 10):" in code
        assert "break" in code


class TestReturnTranslation:
    def test_return_value(self):
        code = _translate("""\
○整数型: foo()
  return 42
""")
        assert "return 42" in code

    def test_return_void(self):
        code = _translate("""\
○display()
  return
""")
        assert "return\n" in code or code.strip().endswith("return")


class TestExpressionTranslation:
    def test_operators(self):
        code = _translate("""\
○整数型: foo()
  return 1 ＋ 2 × 3
""")
        assert "1 + 2 * 3" in code

    def test_boolean_literals(self):
        code = _translate("""\
○整数型: foo()
  if (true)
    return 1
  endif
  return 0
""")
        assert "if True:" in code

    def test_undefined_literal(self):
        code = _translate("""\
○整数型: foo()
  整数型: x ← 未定義の値
  return x
""")
        # 未定義の値 should translate to None
        # The parser may handle this differently; check what's generated
        assert "None" in code

    def test_string_literal(self):
        code = _translate("""\
○foo()
  文字列型: s ← "hello"
  return s
""")
        assert "'hello'" in code or '"hello"' in code

    def test_mod_operator(self):
        code = _translate("""\
○整数型: foo()
  return 10 mod 3
""")
        assert "10 % 3" in code

    def test_array_access(self):
        code = _translate("""\
○整数型: foo()
  整数型の配列: arr ← {1, 2, 3}
  return arr[1]
""")
        assert "arr[1]" in code


class TestJapaneseConditionTranslation:
    def test_ika(self):
        code = _translate("""\
○整数型: foo(整数型: age)
  if (age が 3 以下)
    return 100
  endif
  return 0
""")
        assert "age <= 3" in code

    def test_ijou(self):
        code = _translate("""\
○整数型: foo(整数型: n)
  if (n が 10 以上)
    return 1
  endif
  return 0
""")
        assert "n >= 10" in code

    def test_undefined(self):
        code = _translate("""\
○整数型: foo(整数型: x)
  if (x が 未定義)
    return 0
  endif
  return 1
""")
        assert "x is None" in code

    def test_undefined_not(self):
        code = _translate("""\
○整数型: foo(整数型: x)
  if (x が 未定義でない)
    return 1
  endif
  return 0
""")
        assert "x is not None" in code


class TestJapaneseActionTranslation:
    def test_append(self):
        code = _translate("""\
○foo()
  pnListの末尾にiの値を追加する
""")
        assert ".append(" in code

    def test_swap(self):
        code = _translate("""\
○foo()
  data[i]とdata[j]の値を入れ替える
""")
        # Should have swap pattern: a, b = b, a
        assert "data[i], data[j] = data[j], data[i]" in code

    def test_increment(self):
        code = _translate("""\
○foo()
  countの値を1増やす
""")
        assert "+= 1" in code

    def test_break(self):
        code = _translate("""\
○foo()
  while (true)
    繰返し処理を終了する
  endwhile
""")
        assert "break" in code

    def test_print(self):
        code = _translate("""\
○foo()
  "hello"を出力する
""")
        assert "print(" in code


class TestGlobalVarTranslation:
    def test_global_decl(self):
        code = _translate("""\
大域: 整数型: gCount ← 0
○整数型: foo()
  return gCount
""")
        assert "gCount = 0" in code


class TestPrintAllTranslation:
    """P1: 全要素出力パターンのテスト"""

    def test_print_all_comma(self):
        code = _translate("""\
○foo(整数型の配列: arr)
  arrの全ての要素を先頭から順にコンマ区切りで出力する
""")
        assert 'print(*arr, sep=",")' in code

    def test_print_all_space(self):
        code = _translate("""\
○foo(整数型の配列: data)
  dataの全要素の値を要素番号の順に空白区切りで出力する
""")
        assert 'print(*data, sep=" ")' in code


class TestCharToStringTranslation:
    """P2: 文字→文字列変換パターンのテスト"""

    def test_char_to_string(self):
        code = _translate("""\
○文字列型: foo(文字型: c1, 文字型: c2)
  文字列型: s1 ← c1の1文字だけから成る文字列
  文字列型: s2 ← c2の1文字だけから成る文字列
  return s1
""")
        assert "s1 = str(c1)" in code
        assert "s2 = str(c2)" in code


class TestStringAppendTranslation:
    """P3: 文字列型の append → += 分岐のテスト"""

    def test_string_append_uses_plus_equal(self):
        code = _translate("""\
○文字列型: convert(整数型の配列: arr)
  文字列型: result ← ""
  整数型: i
  for (iを1からarrの要素数まで1ずつ増やす)
    resultの末尾に"X"を追加する
  endfor
  return result
""")
        assert 'result += ' in code
        assert ".append(" not in code

    def test_array_append_unchanged(self):
        code = _translate("""\
○foo(整数型の配列: arr)
  整数型の配列: result ← {}
  arrの末尾に42の値を追加する
""")
        assert ".append(42)" in code


class TestReverseCharTranslation:
    """Tier 2: 逆順文字アクセスのテスト"""

    def test_reverse_char_int(self):
        code = _translate("""\
○整数型: foo(文字列型: s)
  整数型: d ← sの末尾から1番目の文字を整数型に変換した値
  return d
""")
        assert "int(s[-1])" in code

    def test_reverse_char(self):
        code = _translate("""\
○文字型: foo(文字列型: s)
  文字型: c ← sの末尾から2番目の文字
  return c
""")
        assert "s[-2]" in code


class TestPowerExprTranslation:
    """Tier 2: 式による累乗のテスト"""

    def test_power_expr(self):
        code = _translate("""\
○整数型: foo(整数型: i)
  整数型: x ← 2の(i − 1)乗
  return x
""")
        assert "2 ** (i - 1)" in code


class TestAnyEqualTranslation:
    """Tier 2: 存在量化のテスト"""

    def test_any_equal(self):
        code = _translate("""\
○foo(文字列型の配列: arr, 文字列型: target)
  if (arrのいずれかの要素の値がtargetの値と等しい)
    return true
  endif
""")
        assert "any(e == target for e in arr)" in code


class TestNegativeInfinityTranslation:
    """Tier 2: 全角マイナス無限大のテスト"""

    def test_fullwidth_minus_infinity(self):
        code = _translate("""\
○foo()
  実数型: x ← \uff0d∞
  return x
""")
        assert "float('-inf')" in code


class TestSumTranslation:
    """Tier 2: 集約パターンのテスト"""

    def test_sum_all(self):
        code = _translate("""\
○実数型: foo(実数型の二次元配列: data)
  実数型: t ← dataの要素の和
  return t
""")
        assert "sum(data)" in code

    def test_sum_row(self):
        code = _translate("""\
○実数型: foo(実数型の二次元配列: data, 整数型: r)
  実数型: s ← (dataの行番号rの要素の和)
  return s
""")
        assert "sum(data.row(r))" in code

    def test_sum_col(self):
        code = _translate("""\
○実数型: foo(実数型の二次元配列: data, 整数型: c)
  実数型: s ← (dataの列番号cの要素の和)
  return s
""")
        assert "sum(data.col(c))" in code


class TestLineContinuation:
    """Tier 2: 行末演算子による行結合のテスト"""

    def test_trailing_multiply_joins(self):
        code = _translate("""\
○整数型: foo(整数型: a, 整数型: b, 整数型: c)
  整数型: x ← a ×
    b ＋ c
  return x
""")
        assert "a * b + c" in code


class TestCompoundConditionKatsu:
    """Tier 3: かつ/または複合条件のテスト"""

    def test_katsu(self):
        code = _translate("""\
○foo(整数型: a, 整数型: b)
  if (aが0と等しい かつ bが1と等しい)
    return true
  endif
""")
        assert "a == 0 and b == 1" in code

    def test_mataha(self):
        code = _translate("""\
○foo(整数型: a, 整数型: b)
  if (aが0と等しい または bが1と等しい)
    return true
  endif
""")
        assert "a == 0 or b == 1" in code


class TestMimanCondition:
    """Tier 3: 未満条件のテスト"""

    def test_miman(self):
        code = _translate("""\
○foo(整数型: t, 整数型: d)
  while (tがd未満)
    t ← t ＋ 1
  endwhile
""")
        assert "while t < d:" in code


class TestDynArray2DComma:
    """Tier 3: 2D配列カンマ形式のテスト"""

    def test_comma_format(self):
        code = _translate("""\
○foo(整数型: s, 整数型: t)
  整数型の二次元配列: lcsl ← {(s ＋ 1)行, (t ＋ 1)列の未定義の値}
  return lcsl
""")
        assert "Array2D(s + 1, t + 1, init=None)" in code


class TestUniqueSortedTranslation:
    """Tier 3: 重複なく辞書順パターンのテスト"""

    def test_unique_sorted(self):
        code = _translate("""\
○foo()
  文字列型の配列: items ← ordersに含まれる文字列を
    重複なく辞書順に格納した配列
  return items
""")
        assert "sorted(set(s for sub in orders for s in sub))" in code


class TestFilterExcludeTranslation:
    """Tier 3: 複製から除外パターンのテスト"""

    def test_filter_exclude(self):
        code = _translate("""\
○foo(文字列型の配列: items, 文字列型: target)
  文字列型の配列: result ← itemsの複製から値がtargetである
    要素を除いた配列
  return result
""")
        assert "[x for x in items if x != target]" in code
