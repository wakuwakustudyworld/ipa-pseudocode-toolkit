"""IPA擬似言語ツールキット

情報処理技術者試験（ITパスポート試験・基本情報技術者試験・応用情報技術者試験）の
擬似言語を解析・変換するPythonツールキット。
"""

from __future__ import annotations

from .parser.ast_nodes import Program
from .parser.grammar import parse as _parse
from .translator.pseudo_to_python import translate as _translate

__version__ = "0.1.0"


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
