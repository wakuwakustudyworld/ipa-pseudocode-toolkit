"""IPA擬似言語ツールキット

情報処理技術者試験（ITパスポート試験・基本情報技術者試験・応用情報技術者試験）の
擬似言語を解析・変換・実行するPythonツールキット。
"""

from __future__ import annotations

from typing import Any

from .parser.ast_nodes import Program
from .parser.grammar import parse as _parse
from .runtime.executor import ExecutionResult, Executor
from .runtime.trace import TraceTable
from .translator.pseudo_to_python import translate as _translate

__version__ = "0.2.0"


def parse(source: str) -> Program:
    """擬似言語のソースコードをパースしてASTを返す

    Args:
        source: IPA擬似言語のソースコード

    Returns:
        パース結果のプログラムAST
    """
    return _parse(source)


def translate(source: str) -> str:
    """擬似言語のソースコードをPythonコードに変換する

    Args:
        source: IPA擬似言語のソースコード

    Returns:
        Pythonソースコード文字列
    """
    program = _parse(source)
    return _translate(program)


def execute(source: str, trace_enabled: bool = False) -> ExecutionResult:
    """擬似言語のソースコードを直接実行する

    Args:
        source: IPA擬似言語のソースコード
        trace_enabled: トレース記録を有効にするか

    Returns:
        実行結果（出力、戻り値、トレース表など）
    """
    program = _parse(source)
    executor = Executor(trace_enabled=trace_enabled)
    return executor.execute(program)


def call_function(source: str, func_name: str, *args: Any) -> Any:
    """擬似言語で定義された関数を指定引数で呼び出す

    Args:
        source: IPA擬似言語のソースコード（関数定義を含む）
        func_name: 呼び出す関数名
        *args: 関数に渡す引数

    Returns:
        関数の戻り値
    """
    program = _parse(source)
    executor = Executor()
    executor.execute(program)
    return executor.call_function(func_name, *args)


def trace(source: str, watch: list[str] | None = None) -> TraceTable:
    """擬似言語のソースコードを実行し、トレース表を返す

    Args:
        source: IPA擬似言語のソースコード
        watch: トレース対象の変数名リスト（Noneで全変数）

    Returns:
        TraceTable
    """
    program = _parse(source)
    executor = Executor(trace_enabled=True)
    if watch and executor._tracer:
        executor._tracer.set_watch(watch)
    result = executor.execute(program)
    return result.trace
