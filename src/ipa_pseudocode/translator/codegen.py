"""コード生成ユーティリティ

Pythonコード生成時のインデント管理やインポート追跡を行うヘルパー。
"""

from __future__ import annotations


class CodeBuilder:
    """Pythonコード生成ヘルパー"""

    def __init__(self, indent_str: str = "    ") -> None:
        self._lines: list[str] = []
        self._indent_level: int = 0
        self._indent_str: str = indent_str
        self._imports: set[str] = set()

    def add_line(self, line: str) -> None:
        """現在のインデントレベルで行を追加する"""
        self._lines.append(f"{self._indent_str * self._indent_level}{line}")

    def add_blank_line(self) -> None:
        """空行を追加する"""
        self._lines.append("")

    def indent(self) -> None:
        """インデントレベルを1つ増やす"""
        self._indent_level += 1

    def dedent(self) -> None:
        """インデントレベルを1つ減らす"""
        self._indent_level = max(0, self._indent_level - 1)

    def add_import(self, statement: str) -> None:
        """インポート文を追加する（重複排除）"""
        self._imports.add(statement)

    def build(self) -> str:
        """最終的なPythonコードを生成する"""
        result: list[str] = []
        if self._imports:
            for imp in sorted(self._imports):
                result.append(imp)
            result.append("")
        result.extend(self._lines)
        # 末尾の空行を整理
        while result and result[-1] == "":
            result.pop()
        result.append("")  # ファイル末尾に改行
        return "\n".join(result)
