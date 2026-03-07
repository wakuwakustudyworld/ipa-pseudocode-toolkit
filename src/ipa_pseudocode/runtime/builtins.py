"""組込み関数・操作

擬似言語の組込み関数を提供する。
"""

from __future__ import annotations

from typing import Any


# 組込み関数テーブル
BUILTIN_FUNCTIONS: dict[str, Any] = {
    "int": int,
    "float": float,
    "str": str,
    "abs": abs,
    "len": len,
}


def is_builtin(name: str) -> bool:
    """組込み関数かどうかを判定する"""
    return name in BUILTIN_FUNCTIONS


def call_builtin(name: str, args: list[Any]) -> Any:
    """組込み関数を呼び出す"""
    func = BUILTIN_FUNCTIONS[name]
    return func(*args)
