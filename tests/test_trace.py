"""トレース表テスト"""

import ipa_pseudocode


class TestSimpleTrace:
    """基本的なトレース"""

    def test_assignment_trace(self):
        """変数代入のトレース"""
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
整数型: y ← 2
x ← y
""")
        assert table is not None
        assert len(table.steps) > 0
        # 最後のステップで x == 2
        last = table.steps[-1]
        assert last.variables["x"] == 2
        assert last.variables["y"] == 2

    def test_swap_trace(self):
        """set-sample/q01 相当のトレース"""
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
整数型: y ← 2
整数型: z ← 3
x ← y
y ← z
z ← x
""")
        assert table is not None
        last = table.steps[-1]
        assert last.variables["x"] == 2
        assert last.variables["y"] == 3
        assert last.variables["z"] == 2

    def test_watch_specific_vars(self):
        """特定変数のみをトレース"""
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
整数型: y ← 2
整数型: z ← 3
""", watch=["x", "z"])
        for step in table.steps:
            assert "y" not in step.variables


class TestLoopTrace:
    """ループのトレース"""

    def test_for_loop_trace(self):
        result = ipa_pseudocode.execute("""\
整数型: s ← 0
for (i を 1 から 3 まで 1 ずつ増やす)
  s ← s ＋ i
endfor
""", trace_enabled=True)
        assert result.trace is not None
        assert result.global_vars["s"] == 6


class TestTraceOutput:
    """トレース表の出力形式"""

    def test_to_markdown(self):
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
整数型: y ← 2
""")
        md = table.to_markdown()
        assert "| Step |" in md
        assert "| --- |" in md

    def test_to_csv(self):
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
""")
        csv_str = table.to_csv()
        assert "Step" in csv_str

    def test_to_dict(self):
        table = ipa_pseudocode.trace("""\
整数型: x ← 1
""")
        dicts = table.to_dict()
        assert len(dicts) > 0
        assert "step" in dicts[0]
        assert "variables" in dicts[0]


class TestFunctionTrace:
    """関数呼び出しのトレース"""

    def test_function_call_trace(self):
        """関数呼び出しをcall_function経由でトレース"""
        source = """\
○整数型: double(整数型: x)
  return x × 2
"""
        program = ipa_pseudocode.parse(source)
        from ipa_pseudocode.runtime.executor import Executor

        executor = Executor(trace_enabled=True)
        executor.execute(program)
        result = executor.call_function("double", 5)
        assert result == 10
        # call イベントが記録されている
        table = executor._tracer.build_table()
        events = [s.event for s in table.steps]
        assert "call" in events
