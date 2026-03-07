"""統合テスト: 擬似言語→Python→実行→結果検証"""

import ipa_pseudocode


class TestFeeFunction:
    """入場料金関数（if/elseif/else）"""

    SOURCE = """\
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

    def test_translate_and_execute(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["fee"](2) == 100
        assert ns["fee"](3) == 100
        assert ns["fee"](5) == 300
        assert ns["fee"](9) == 300
        assert ns["fee"](15) == 500


class TestSumFunction:
    """合計関数（forループ）"""

    SOURCE = """\
○整数型: total(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす)
    s ← s ＋ i
  endfor
  return s
"""

    def test_sum_1_to_10(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["total"](10) == 55

    def test_sum_1_to_100(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["total"](100) == 5050


class TestMaxFunction:
    """最大値検索（for＋if）"""

    SOURCE = """\
○整数型: findMax(整数型の配列: arr, 整数型: n)
  整数型: maxVal ← arr[1]
  for (i を 2 から n まで 1 ずつ増やす)
    if (arr[i] ＞ maxVal)
      maxVal ← arr[i]
    endif
  endfor
  return maxVal
"""

    def test_find_max(self):
        from ipa_pseudocode.core.array import Array

        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        arr = Array.from_literal([3, 7, 2, 9, 1])
        assert ns["findMax"](arr, 5) == 9


class TestCountdownFunction:
    """カウントダウン（デクリメントforループ）"""

    SOURCE = """\
○整数型: countdown(整数型: n)
  整数型: s ← 0
  for (i を n から 1 まで 1 ずつ減らす)
    s ← s ＋ i
  endfor
  return s
"""

    def test_countdown(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        # sum from n down to 1 is the same as 1 to n
        assert ns["countdown"](10) == 55


class TestWhileLoop:
    """whileループのテスト"""

    SOURCE = """\
○整数型: countUp(整数型: limit)
  整数型: i ← 0
  while (i ＜ limit)
    i ← i ＋ 1
  endwhile
  return i
"""

    def test_while_loop(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["countUp"](5) == 5
        assert ns["countUp"](0) == 0


class TestDoWhileLoop:
    """do-whileループのテスト"""

    SOURCE = """\
○整数型: doCount()
  整数型: i ← 0
  do
    i ← i ＋ 1
  while (i ＜ 5)
  return i
"""

    def test_do_while(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["doCount"]() == 5


class TestFactorial:
    """階乗（再帰）"""

    SOURCE = """\
○整数型: factorial(整数型: n)
  if (n ≦ 1)
    return 1
  endif
  return n × factorial(n − 1)
"""

    def test_factorial(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["factorial"](5) == 120
        assert ns["factorial"](0) == 1
        assert ns["factorial"](1) == 1


class TestModOperator:
    """mod演算子"""

    SOURCE = """\
○整数型: isEven(整数型: n)
  if (n mod 2 ＝ 0)
    return 1
  endif
  return 0
"""

    def test_mod(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["isEven"](4) == 1
        assert ns["isEven"](7) == 0


class TestBooleanLogic:
    """論理演算"""

    SOURCE = """\
○整数型: inRange(整数型: x, 整数型: lo, 整数型: hi)
  if (x ≧ lo and x ≦ hi)
    return 1
  endif
  return 0
"""

    def test_and_logic(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["inRange"](5, 1, 10) == 1
        assert ns["inRange"](0, 1, 10) == 0
        assert ns["inRange"](11, 1, 10) == 0


class TestGlobalVariable:
    """グローバル変数"""

    SOURCE = """\
大域: 整数型: gCount ← 0
○整数型: getCount()
  return gCount
"""

    def test_global_var(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["getCount"]() == 0


class TestIntegerDivision:
    """整数除算（÷...の商）"""

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
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["change"](26) == 12

    def test_change_10(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["change"](10) == 4

    def test_change_0(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["change"](0) == 1

    def test_integer_division_in_code(self):
        """変換結果に // が含まれることを確認"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "//" in code
        assert "rest // 5" in code

    def test_katakana_minus_in_code(self):
        """ー (U+30FC) がマイナスとして変換されることを確認"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "rest - 10" in code


class TestStackOperations:
    """スタック操作（大域変数、未定義の値、要素数）"""

    SOURCE = """\
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

    def test_undefined_in_array_literal(self):
        """配列リテラル内の「未定義の値」が None に変換される"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "Array.from_literal([4, 3, None, None])" in code

    def test_element_count(self):
        """「stackの要素数」が len(stack) に変換される"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "len(stack)" in code

    def test_global_declaration(self):
        """大域変数への代入時に global 宣言が追加される"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "global stackPos" in code
        assert "global stack" in code

    def test_push_and_pop(self):
        """push/popが正しく動作する"""
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        # push
        assert ns["push"](7) is True
        assert ns["stackPos"] == 4
        assert ns["stack"][3] == 7
        # pop
        assert ns["pop"]() == 7
        assert ns["stackPos"] == 3


class TestParenthesization:
    """二項演算の括弧付け"""

    SOURCE = """\
○整数型: search(整数型の配列: data, 整数型: target)
  整数型: low ← 1
  整数型: high ← dataの要素数
  整数型: middle ← (low ＋ high) ÷ 2の商
  return middle
"""

    def test_parenthesization(self):
        """(low + high) // 2 のように括弧が正しく付く"""
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "(low + high) // 2" in code


class TestDynamicArrayInit:
    """動的配列初期化 {n個のX}, {n行m列のX}"""

    SOURCE_1D = """\
○整数型の配列: makeArray(整数型: n)
  整数型の配列: arr ← {n個の0}
  return arr
"""

    SOURCE_2D = """\
○整数型の二次元配列: makeMatrix(整数型: rows, 整数型: cols)
  整数型の二次元配列: mat ← {rows行cols列の0}
  return mat
"""

    SOURCE_COMPOUND = """\
○整数型の配列: makeWork(整数型: n1, 整数型: n2)
  整数型の配列: work ← {(n1＋n2)個の未定義の値}
  return work
"""

    def test_1d_dynamic_array(self):
        code = ipa_pseudocode.translate(self.SOURCE_1D)
        assert "Array(n, init=0)" in code

    def test_2d_dynamic_array(self):
        code = ipa_pseudocode.translate(self.SOURCE_2D)
        assert "Array2D(rows, cols, init=0)" in code

    def test_compound_size(self):
        """(n1+n2)個の場合"""
        code = ipa_pseudocode.translate(self.SOURCE_COMPOUND)
        assert "Array(n1 + n2, init=None)" in code

    def test_1d_execute(self):
        code = ipa_pseudocode.translate(self.SOURCE_1D)
        ns: dict = {}
        exec(code, ns)
        result = ns["makeArray"](5)
        from ipa_pseudocode.core.array import Array
        assert isinstance(result, Array)
        assert len(result) == 5
        assert result[1] == 0


class TestInlineComments:
    """インラインコメント // の除去"""

    SOURCE = """\
○整数型: sumWithComment(整数型: n)
  整数型: s ← 0
  for (i を 1 から n まで 1 ずつ増やす) // ループ
    s ← s ＋ i
  endfor
  return s
"""

    def test_inline_comment_stripped(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["sumWithComment"](10) == 55


class TestModuloOperator:
    """÷ X の余り → % 演算子"""

    SOURCE = """\
○整数型: remainder(整数型: a, 整数型: b)
  return a ÷ b の余り
"""

    def test_modulo(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "a % b" in code

    def test_modulo_execute(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        ns: dict = {}
        exec(code, ns)
        assert ns["remainder"](10, 3) == 1
        assert ns["remainder"](15, 5) == 0


class TestPropertyAccessPostfix:
    """expr の要素数 （後置プロパティアクセス）"""

    SOURCE = """\
○整数型: getLen(整数型の配列: arr)
  整数型の配列: nested ← {{1, 2}, {3, 4}}
  return arr[1]
"""

    def test_postfix_property_in_condition(self):
        """tree[n]の要素数 のような後置プロパティが正しく変換される"""
        src = """\
大域: 整数型配列の配列: tree ← {{2, 3}, {4}, {}}
○整数型: countChildren(整数型: n)
  return tree[n]の要素数
"""
        code = ipa_pseudocode.translate(src)
        assert "len(tree[n])" in code


class TestMultiLineContinuation:
    """複数行にまたがる配列リテラル・関数定義"""

    SOURCE = """\
○整数型: test(整数型の配列: a,
              整数型: n)
  return a[1] ＋ n
"""

    def test_multiline_function_def(self):
        code = ipa_pseudocode.translate(self.SOURCE)
        assert "def test(a, n):" in code

    def test_multiline_array_literal(self):
        src = """\
大域: 整数型の配列: data ← {1, 2,
                          3, 4}
"""
        code = ipa_pseudocode.translate(src)
        assert "Array.from_literal([1, 2, 3, 4])" in code


class TestPublicAPI:
    """公開API（parse/translate）のテスト"""

    def test_parse(self):
        prog = ipa_pseudocode.parse("○整数型: foo()\n  return 1\n")
        assert len(prog.functions) == 1
        assert prog.functions[0].name == "foo"

    def test_translate(self):
        code = ipa_pseudocode.translate("○整数型: foo()\n  return 1\n")
        assert "def foo():" in code
        assert "return 1" in code

    def test_version(self):
        assert ipa_pseudocode.__version__ == "0.3.0"


class TestCharAtPattern:
    """CharAtパターン: Xのi文字目の文字"""

    def test_char_at_inline(self):
        code = ipa_pseudocode.translate("""\
○整数型: f(文字列型: binary)
  整数型: result ← 0
  整数型: i, length
  length ← binaryの文字数
  for (iを 1 から lengthまで 1 ずつ増やす)
    result ← result × 2 ＋ int(binaryのi文字目の文字)
  endfor
  return result
""")
        assert "binary[i - 1]" in code
        assert "int(binary[i - 1])" in code

    def test_char_at_postfix(self):
        """配列アクセス後のCharAtパターン"""
        code = ipa_pseudocode.translate("""\
○f(文字列型の配列: arr)
  return arr[1]の3文字目の文字
""")
        assert "arr[1][3 - 1]" in code


class TestMathPatterns:
    """数学パターン: の2乗, の正の平方根, の正の平方根の整数部分"""

    def test_square(self):
        code = ipa_pseudocode.translate("""\
○f(整数型: n)
  return nの2乗
""")
        assert "n ** 2" in code

    def test_square_postfix_array(self):
        """配列アクセス後のの2乗"""
        code = ipa_pseudocode.translate("""\
○f(整数型の配列: v)
  整数型: i
  実数型: temp ← 0
  for (iを 1 から vの要素数 まで 1 ずつ増やす)
    temp ← temp ＋ v[i]の2乗
  endfor
  return temp
""")
        assert "v[i] ** 2" in code

    def test_sqrt(self):
        code = ipa_pseudocode.translate("""\
○f(実数型: x)
  return xの正の平方根
""")
        assert "x ** 0.5" in code

    def test_sqrt_int_part(self):
        code = ipa_pseudocode.translate("""\
○f(整数型: n)
  return nの正の平方根の整数部分
""")
        assert "int(n ** 0.5)" in code

    def test_cosine_similarity_pattern(self):
        """コサイン類似度パターン（の2乗 + の正の平方根の組み合わせ）"""
        code = ipa_pseudocode.translate("""\
○f(実数型の配列: v)
  実数型: temp ← 0
  整数型: i
  for (iを 1 から vの要素数 まで 1 ずつ増やす)
    temp ← temp ＋ v[i]の2乗
  endfor
  実数型: result ← tempの正の平方根
  return result
""")
        assert "v[i] ** 2" in code
        assert "temp ** 0.5" in code


class TestPrintWithoutSuru:
    """出力パターン: Xを出力（するなし）"""

    def test_print_without_suru(self):
        code = ipa_pseudocode.translate("""\
○f(整数型: n)
  nを出力
""")
        assert "print(n)" in code

    def test_print_with_suru(self):
        code = ipa_pseudocode.translate("""\
○f(整数型: n)
  nを出力する
""")
        assert "print(n)" in code


class TestSafeNameKeywords:
    """Python予約語の回避"""

    def test_in_parameter(self):
        code = ipa_pseudocode.translate("""\
○f(整数型の配列: in)
  return in[1]
""")
        assert "def f(in_):" in code
        assert "return in_[1]" in code

    def test_builtin_not_renamed(self):
        """Python組込み名(int等)は関数呼び出しとして使われるのでリネームしない"""
        code = ipa_pseudocode.translate("""\
○f(文字列型: s)
  return int(s)
""")
        assert "int(s)" in code
        assert "int_" not in code


class TestArrayBasedExecution:
    """Array クラスを使った1-based配列の動作検証"""

    def test_array_literal_1based(self):
        """配列リテラルが Array.from_literal で出力され、1-basedでアクセスできる"""
        code = ipa_pseudocode.translate("""\
大域: 整数型の配列: data ← {10, 20, 30}

○整数型: first()
  return data[1]
""")
        assert "Array.from_literal" in code
        ns: dict = {}
        exec(code, ns)
        result = ns["first"]()
        assert result == 10

    def test_array_init_1based(self):
        """動的配列初期化が Array で出力され、1-basedでアクセスできる"""
        code = ipa_pseudocode.translate("""\
○整数型の配列: makeAndSet(整数型: n)
  整数型の配列: arr ← {n個の0}
  arr[1] ← 99
  arr[n] ← 88
  return arr
""")
        ns: dict = {}
        exec(code, ns)
        result = ns["makeAndSet"](3)
        assert result[1] == 99
        assert result[3] == 88
        assert result[2] == 0

    def test_array2d_init(self):
        """2D動的配列初期化が Array2D で出力される"""
        code = ipa_pseudocode.translate("""\
○f(整数型: rows, 整数型: cols)
  整数型の二次元配列: mat ← {rows行cols列の0}
  mat[1, 1] ← 42
  return mat
""")
        assert "Array2D" in code
        ns: dict = {}
        exec(code, ns)
        result = ns["f"](2, 3)
        assert result[1, 1] == 42
        assert result[2, 3] == 0

    def test_array_import_injected(self):
        """Array 使用時に import 文が自動挿入される"""
        code = ipa_pseudocode.translate("""\
大域: 整数型の配列: data ← {1, 2, 3}
""")
        assert "from ipa_pseudocode.core.array import Array" in code

    def test_array2d_import_injected(self):
        """Array2D 使用時に import 文が自動挿入される"""
        code = ipa_pseudocode.translate("""\
○f()
  整数型の二次元配列: mat ← {2行3列の0}
  return mat
""")
        assert "from ipa_pseudocode.core.array import Array2D" in code

    def test_no_import_when_no_array(self):
        """配列を使わない場合は import が挿入されない"""
        code = ipa_pseudocode.translate("""\
○整数型: add(整数型: a, 整数型: b)
  return a ＋ b
""")
        assert "import" not in code

    def test_swap_with_array(self):
        """Array を使った入れ替えが正しく動作する"""
        code = ipa_pseudocode.translate("""\
○f(整数型の配列: arr)
  arr[1]とarr[2]の値を入れ替える
""")
        ns: dict = {}
        exec(code, ns)
        from ipa_pseudocode.core.array import Array
        arr = Array.from_literal([10, 20, 30])
        ns["f"](arr)
        assert arr[1] == 20
        assert arr[2] == 10

    def test_append_with_array(self):
        """Array を使った末尾追加が正しく動作する"""
        code = ipa_pseudocode.translate("""\
○f(整数型の配列: arr, 整数型: val)
  arrの末尾にvalの値を追加する
""")
        ns: dict = {}
        exec(code, ns)
        from ipa_pseudocode.core.array import Array
        arr = Array.from_literal([1, 2])
        ns["f"](arr, 3)
        assert len(arr) == 3
        assert arr[3] == 3

    def test_foreach_with_array(self):
        """Array に対する for-each が正しく動作する"""
        code = ipa_pseudocode.translate("""\
○整数型: sumAll(整数型の配列: arr)
  整数型: total ← 0
  整数型: x
  for (x に arr の要素を順に代入する)
    total ← total ＋ x
  endfor
  return total
""")
        ns: dict = {}
        exec(code, ns)
        from ipa_pseudocode.core.array import Array
        result = ns["sumAll"](Array.from_literal([10, 20, 30]))
        assert result == 60
