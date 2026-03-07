"""トレース表（実行過程の記録）

擬似言語の実行過程を記録し、変数の変化をトレース表として出力する。
IPA試験のトレース問題の自動解答・解説生成に活用する。
"""

from __future__ import annotations

import copy
import csv
import io
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceStep:
    """トレース表の1ステップ"""

    step_number: int
    line_description: str  # 実行した文の説明
    variables: dict[str, Any]  # この時点の変数スナップショット
    scope: str  # "global" or 関数名
    event: str  # "assign" | "call" | "return" | "branch" | "loop" | "output"
    detail: str = ""  # 補足情報
    output: str | None = None  # 出力がある場合


@dataclass
class TraceTable:
    """トレース表"""

    steps: list[TraceStep] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)  # トレース対象の変数名

    def to_markdown(self) -> str:
        """Markdownテーブル形式で出力する"""
        if not self.steps:
            return ""

        # 列を決定
        cols = self.columns if self.columns else self._detect_columns()

        # ヘッダ
        header = ["Step", "文"] + cols + ["出力"]
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]

        # 各ステップ
        for step in self.steps:
            row = [str(step.step_number), step.line_description]
            for col in cols:
                val = step.variables.get(col)
                row.append(_format_value(val) if col in step.variables else "-")
            row.append(step.output if step.output else "")
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def to_csv(self) -> str:
        """CSV形式で出力する"""
        if not self.steps:
            return ""

        cols = self.columns if self.columns else self._detect_columns()
        output = io.StringIO()
        writer = csv.writer(output)

        header = ["Step", "文"] + cols + ["出力"]
        writer.writerow(header)

        for step in self.steps:
            row = [str(step.step_number), step.line_description]
            for col in cols:
                val = step.variables.get(col)
                row.append(_format_value(val) if col in step.variables else "")
            row.append(step.output if step.output else "")
            writer.writerow(row)

        return output.getvalue()

    def to_dict(self) -> list[dict[str, Any]]:
        """辞書のリストとして返す"""
        return [
            {
                "step": s.step_number,
                "line": s.line_description,
                "variables": dict(s.variables),
                "scope": s.scope,
                "event": s.event,
                "detail": s.detail,
                "output": s.output,
            }
            for s in self.steps
        ]

    def _detect_columns(self) -> list[str]:
        """全ステップから変数名を収集する（出現順）"""
        seen: dict[str, None] = {}
        for step in self.steps:
            for name in step.variables:
                if name not in seen:
                    seen[name] = None
        return list(seen.keys())


class Tracer:
    """Executor に組み込まれるトレース記録コンポーネント"""

    def __init__(self) -> None:
        self._steps: list[TraceStep] = []
        self._step_counter: int = 0
        self._watched_vars: set[str] | None = None

    def set_watch(self, var_names: list[str]) -> None:
        """特定の変数のみを記録対象にする"""
        self._watched_vars = set(var_names)

    def record(
        self,
        description: str,
        variables: dict[str, Any],
        scope: str,
        event: str,
        detail: str = "",
        output: str | None = None,
    ) -> None:
        """1ステップを記録する"""
        self._step_counter += 1

        # 変数のスナップショットを取る
        if self._watched_vars is not None:
            snapshot = {
                k: _deep_copy_value(v)
                for k, v in variables.items()
                if k in self._watched_vars
            }
        else:
            snapshot = {k: _deep_copy_value(v) for k, v in variables.items()}

        self._steps.append(
            TraceStep(
                step_number=self._step_counter,
                line_description=description,
                variables=snapshot,
                scope=scope,
                event=event,
                detail=detail,
                output=output,
            )
        )

    def build_table(self, columns: list[str] | None = None) -> TraceTable:
        """記録したステップからTraceTableを構築する"""
        table = TraceTable(steps=self._steps)
        if columns:
            table.columns = columns
        return table


def _deep_copy_value(val: Any) -> Any:
    """値のディープコピー（配列のスナップショット用）"""
    try:
        return copy.deepcopy(val)
    except Exception:
        return val


def _format_value(val: Any) -> str:
    """トレース表示用に値をフォーマットする"""
    if val is None:
        return "未定義"
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)
