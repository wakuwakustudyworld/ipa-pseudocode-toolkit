"""Executor テスト: 擬似言語の直接実行"""

import pytest

import ipa_pseudocode
from ipa_pseudocode.core.array import Array, Array2D
from ipa_pseudocode.runtime.executor import Executor


class TestBasicExecution:
    """基本的な変数宣言・代入・参照"""

    def test_var_decl_and_assign(self):
        result = ipa_pseudocode.execute("""\
整数型: x ← 42
""")
        assert result.global_vars["x"] == 42

    def test_multiple_var_decl(self):
        result = ipa_pseudocode.execute("""\
整数型: a, b
a ← 1
b ← 2
""")
        assert result.global_vars["a"] == 1
        assert result.global_vars["b"] == 2

    def test_undefined_value(self):
        result = ipa_pseudocode.execute("""\
整数型: x ← 未定義の値
""")
        assert result.global_vars["x"] is None


class TestArithmetic:
    """四則演算・比較・論理"""

    def test_addition(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f()
  return 3 ＋ 4
""", "f")
        assert val == 7

    def test_subtraction(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f()
  return 10 − 3
""", "f")
        assert val == 7

    def test_multiplication(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f()
  return 6 × 7
""", "f")
        assert val == 42

    def test_division(self):
        val = ipa_pseudocode.call_function("""\
○実数型: f()
  return 10 ÷ 3
""", "f")
        assert abs(val - 10 / 3) < 1e-10

    def test_integer_division(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f()
  return 10 ÷ 3の商
""", "f")
        assert val == 3

    def test_mod(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f()
  return 10 mod 3
""", "f")
        assert val == 1

    def test_modulo_余り(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(整数型: a, 整数型: b)
  return a ÷ b の余り
""", "f", 10, 3)
        assert val == 1

    def test_comparison(self):
        val = ipa_pseudocode.call_function("""\
○論理型: f()
  return 3 ＜ 5
""", "f")
        assert val is True

    def test_boolean_and(self):
        val = ipa_pseudocode.call_function("""\
○整数型: inRange(整数型: x, 整数型: lo, 整数型: hi)
  if (x ≧ lo and x ≦ hi)
    return 1
  endif
  return 0
""", "inRange", 5, 1, 10)
        assert val == 1

    def test_boolean_and_false(self):
        val = ipa_pseudocode.call_function("""\
○整数型: inRange(整数型: x, 整数型: lo, 整数型: hi)
  if (x ≧ lo and x ≦ hi)
    return 1
  endif
  return 0
""", "inRange", 0, 1, 10)
        assert val == 0


class TestControlFlow:
    """制御フロー"""

    def test_if_then(self):
        val = ipa_pseudocode.call_function("""\
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
""", "fee", 2)
        assert val == 100

    def test_if_elseif(self):
        val = ipa_pseudocode.call_function("""\
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
""", "fee", 5)
        assert val == 300

    def test_if_else(self):
        val = ipa_pseudocode.call_function("""\
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
""", "fee", 15)
        assert val == 500

    def test_while_loop(self):
        val = ipa_pseudocode.call_function("""\
○整数型: countUp(整数型: limit)
  整数型: i ← 0
  while (i ＜ limit)
    i ← i ＋ 1
  endwhile
  return i
""", "countUp", 5)
        assert val == 5

    def test_while_zero(self):
        val = ipa_pseudocode.call_function("""\
○整数型: countUp(整数型: limit)
  整数型: i ← 0
  while (i ＜ limit)
    i ← i ＋ 1
  endwhile
  return i
""", "countUp", 0)
        assert val == 0

    def test_do_while(self):
        val = ipa_pseudocode.call_function("""\
○整数型: doCount()
  整数型: i ← 0
  do
    i ← i ＋ 1
  while (i ＜ 5)
  return i
""", "doCount")
        assert val == 5

    def test_for_increment(self):
        val = ipa_pseudocode.call_function("""\
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
""", "total", 10)
        assert val == 55

    def test_for_decrement(self):
        val = ipa_pseudocode.call_function("""\
○整数型: countdown(整数型: n)
  整数型: s ← 0
  for (i を n から 1 まで 1 ずつ減らす)
    s ← s ＋ i
  endfor
  return s
""", "countdown", 10)
        assert val == 55

    def test_for_each(self):
        val = ipa_pseudocode.call_function("""\
○整数型: sumAll(整数型の配列: arr)
  整数型: total ← 0
  整数型: x
  for (x に arr の要素を順に代入する)
    total ← total ＋ x
  endfor
  return total
""", "sumAll", Array.from_literal([10, 20, 30]))
        assert val == 60


class TestFunctions:
    """関数呼び出し・再帰"""

    def test_simple_function(self):
        val = ipa_pseudocode.call_function("""\
○整数型: add(整数型: a, 整数型: b)
  return a ＋ b
""", "add", 3, 4)
        assert val == 7

    def test_recursion(self):
        val = ipa_pseudocode.call_function("""\
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
""", "factorial", 5)
        assert val == 120

    def test_recursion_base(self):
        val = ipa_pseudocode.call_function("""\
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
""", "factorial", 0)
        assert val == 1

    def test_multiple_functions(self):
        val = ipa_pseudocode.call_function("""\
○整数型: double(整数型: x)
  return x × 2

○整数型: quadruple(整数型: x)
  return double(double(x))
""", "quadruple", 3)
        assert val == 12


class TestGlobalVariables:
    """グローバル変数"""

    def test_global_read(self):
        val = ipa_pseudocode.call_function("""\
大域: 整数型: gCount ← 0
○整数型: getCount()
  return gCount
""", "getCount")
        assert val == 0

    def test_global_write(self):
        source = """\
大域: 整数型: gCount ← 0
○increment()
  gCount ← gCount ＋ 1
"""
        program = ipa_pseudocode.parse(source)
        executor = Executor()
        executor.execute(program)
        executor.call_function("increment")
        executor.call_function("increment")
        assert executor._global_scope["gCount"] == 2

    def test_stack_operations(self):
        """スタック操作（大域変数、未定義の値、要素数）"""
        source = """\
大域: 整数型: stackPos ← 3
大域: 整数型の配列 : stack ← {4, 3,未定義の値, 未定義の値 }

○論理型: push(整数型: inputData)
　if (stackPos ≦ stackの要素数)
　　stack[stackPos] ← inputData
　　stackPos ← stackPos＋ 1
　　return true
　else
　　return false
　endif

○整数型: pop()
　整数型: popData ←未定義の値
　if (stackPos＞ 1)
　　stackPos ← stackPos− 1
　　popData ← stack[stackPos]
　　stack[stackPos] ←未定義の値
　endif
　return popData
"""
        program = ipa_pseudocode.parse(source)
        executor = Executor()
        executor.execute(program)
        assert executor.call_function("push", 7) is True
        assert executor._global_scope["stackPos"] == 4
        assert executor._global_scope["stack"][3] == 7
        assert executor.call_function("pop") == 7
        assert executor._global_scope["stackPos"] == 3


class TestArrays:
    """配列操作"""

    def test_array_1based(self):
        val = ipa_pseudocode.call_function("""\
○整数型: first(整数型の配列: arr)
  return arr[1]
""", "first", Array.from_literal([10, 20, 30]))
        assert val == 10

    def test_array_literal(self):
        result = ipa_pseudocode.execute("""\
整数型の配列: data ← {10, 20, 30}
""")
        arr = result.global_vars["data"]
        assert isinstance(arr, Array)
        assert arr[1] == 10
        assert arr[3] == 30

    def test_find_max(self):
        val = ipa_pseudocode.call_function("""\
○整数型: findMax(整数型の配列: arr, 整数型: n)
  整数型: maxVal ← arr[1]
  for (i を 2 から n まで 1 ずつ増やす)
    if (arr[i] ＞ maxVal)
      maxVal ← arr[i]
    endif
  endfor
  return maxVal
""", "findMax", Array.from_literal([3, 7, 2, 9, 1]), 5)
        assert val == 9

    def test_dynamic_array_1d(self):
        val = ipa_pseudocode.call_function("""\
○整数型の配列: makeArray(整数型: n)
  整数型の配列: arr ← {n個の0}
  arr[1] ← 99
  return arr
""", "makeArray", 5)
        assert isinstance(val, Array)
        assert len(val) == 5
        assert val[1] == 99
        assert val[2] == 0

    def test_dynamic_array_2d(self):
        val = ipa_pseudocode.call_function("""\
○f(整数型: rows, 整数型: cols)
  整数型の二次元配列: mat ← {rows行cols列の0}
  mat[1, 1] ← 42
  return mat
""", "f", 2, 3)
        assert isinstance(val, Array2D)
        assert val[1, 1] == 42
        assert val[2, 3] == 0

    def test_swap(self):
        arr = Array.from_literal([10, 20, 30])
        ipa_pseudocode.call_function("""\
○f(整数型の配列: arr)
  arr[1]とarr[2]の値を入れ替える
""", "f", arr)
        assert arr[1] == 20
        assert arr[2] == 10

    def test_append(self):
        arr = Array.from_literal([1, 2])
        ipa_pseudocode.call_function("""\
○f(整数型の配列: arr, 整数型: val)
  arrの末尾にvalの値を追加する
""", "f", arr, 3)
        assert len(arr) == 3
        assert arr[3] == 3


class TestPropertyAccess:
    """プロパティアクセス"""

    def test_array_length(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(整数型の配列: arr)
  return arrの要素数
""", "f", Array.from_literal([1, 2, 3]))
        assert val == 3

    def test_string_length(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(文字列型: s)
  return sの文字数
""", "f", "hello")
        assert val == 5

    def test_char_at(self):
        val = ipa_pseudocode.call_function("""\
○文字型: f(文字列型: s)
  return sの2文字目の文字
""", "f", "hello")
        assert val == "e"


class TestMathPatterns:
    """数学パターン"""

    def test_square(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(整数型: n)
  return nの2乗
""", "f", 5)
        assert val == 25

    def test_sqrt(self):
        val = ipa_pseudocode.call_function("""\
○実数型: f(実数型: x)
  return xの正の平方根
""", "f", 9.0)
        assert val == 3.0

    def test_sqrt_int_part(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(整数型: n)
  return nの正の平方根の整数部分
""", "f", 10)
        assert val == 3


class TestPrint:
    """出力"""

    def test_simple_print(self):
        result = ipa_pseudocode.execute("""\
整数型: x ← 42
xを出力する
""")
        assert result.output == ["42"]

    def test_print_separator(self):
        result = ipa_pseudocode.execute("""\
整数型: x ← 1
整数型: y ← 2
整数型: z ← 3
yの値と zの値をこの順にコンマ区切りで出力する
""")
        assert len(result.output) == 1
        assert "," in result.output[0]


class TestIntegerDivision:
    """整数除算（÷...の商）+ カタカナマイナス"""

    SOURCE = """\
○整数型: change(整数型: n)
　整数型: count ← 0
　整数型: rest ← n
　while ( rest ≧ 0 )
　　count ← count ＋ (rest ÷ 5の商)＋ 1
　　rest ← rest ー 10
　endwhile
　return count
"""

    def test_change_26(self):
        val = ipa_pseudocode.call_function(self.SOURCE, "change", 26)
        assert val == 12

    def test_change_10(self):
        val = ipa_pseudocode.call_function(self.SOURCE, "change", 10)
        assert val == 4

    def test_change_0(self):
        val = ipa_pseudocode.call_function(self.SOURCE, "change", 0)
        assert val == 1


class TestIncrementStatement:
    """値の増減"""

    def test_increment(self):
        result = ipa_pseudocode.execute("""\
整数型: x ← 10
xの値を3増やす
""")
        assert result.global_vars["x"] == 13


class TestExamQuestion:
    """試験問題レベルの統合テスト"""

    def test_make_new_array(self):
        """累積和配列の生成"""
        val = ipa_pseudocode.call_function("""\
○整数型の配列: makeNewArray(整数型の配列: in)
  整数型の配列: out ← {}
  整数型: i, tail
  outの末尾に in[1]の値を追加する
  for (i を 2 から inの要素数 まで 1 ずつ増やす)
    tail ← out[outの要素数]
    outの末尾に (tail ＋ in[i]) の値を追加する
  endfor
  return out
""", "makeNewArray", Array.from_literal([1, 2, 3, 4]))
        assert val.to_list() == [1, 3, 6, 10]


class TestEdgeCases:
    """エッジケース"""

    def test_negative_infinity(self):
        val = ipa_pseudocode.call_function("""\
○実数型: f()
  return −∞
""", "f")
        assert val == float("-inf")

    def test_max_steps_exceeded(self):
        with pytest.raises(RuntimeError, match="最大ステップ数"):
            program = ipa_pseudocode.parse("""\
整数型: x ← 0
while (x ＝ 0)
  x ← 0
endwhile
""")
            executor = Executor(max_steps=100)
            executor.execute(program)

    def test_undefined_variable_error(self):
        with pytest.raises(RuntimeError, match="定義されていません"):
            ipa_pseudocode.call_function("""\
○整数型: f()
  return undefined_var
""", "f")

    def test_undefined_function_error(self):
        with pytest.raises(RuntimeError, match="定義されていません"):
            ipa_pseudocode.call_function("""\
○整数型: f()
  return 1
""", "nonexistent")


class TestBuiltinFunctions:
    """組込み関数"""

    def test_int_conversion(self):
        val = ipa_pseudocode.call_function("""\
○整数型: f(文字列型: s)
  return int(s)
""", "f", "42")
        assert val == 42
