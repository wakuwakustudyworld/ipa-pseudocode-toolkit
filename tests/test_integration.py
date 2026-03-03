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
        assert ipa_pseudocode.__version__ == "0.1.0"
