"""IPA擬似言語の型定義

擬似言語で使用される型名（整数型、実数型、文字列型等）の解析と表現を提供する。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class IPAType(Enum):
    """IPA擬似言語の基本型"""

    INTEGER = "整数型"
    REAL = "実数型"
    STRING = "文字列型"
    CHAR = "文字型"
    BOOLEAN = "論理型"
    CUSTOM = "custom"


@dataclass(frozen=True)
class TypeInfo:
    """解析された型情報

    Attributes:
        base_type: 基本型
        is_array: 一次元配列かどうか
        is_2d_array: 二次元配列かどうか
        is_array_of_arrays: 配列の配列かどうか
        class_name: カスタム型の場合のクラス名
        raw: 元の型注釈文字列
    """

    base_type: IPAType
    is_array: bool = False
    is_2d_array: bool = False
    is_array_of_arrays: bool = False
    class_name: str | None = None
    raw: str = ""

    @property
    def python_type_hint(self) -> str:
        """Python型ヒント文字列を返す"""
        base = _IPA_TO_PYTHON_TYPE.get(self.base_type, "Any")
        if self.class_name:
            base = self.class_name
        if self.is_2d_array:
            return f"list[list[{base}]]"
        if self.is_array_of_arrays:
            return f"list[list[{base}]]"
        if self.is_array:
            return f"list[{base}]"
        return base


_IPA_TO_PYTHON_TYPE: dict[IPAType, str] = {
    IPAType.INTEGER: "int",
    IPAType.REAL: "float",
    IPAType.STRING: "str",
    IPAType.CHAR: "str",
    IPAType.BOOLEAN: "bool",
}

# 型名プレフィックスから IPAType への対応
_TYPE_PREFIX_MAP: dict[str, IPAType] = {
    "整数": IPAType.INTEGER,
    "実数": IPAType.REAL,
    "文字列": IPAType.STRING,
    "文字": IPAType.CHAR,
    "論理": IPAType.BOOLEAN,
}

# 型注釈の解析パターン（優先順位の高い順）
_ARRAY_OF_ARRAYS_RE = re.compile(r"^(.+?)型?配列の配列$")
_2D_ARRAY_RE = re.compile(r"^(.+?)型?の二次元配列$")
_ARRAY_RE = re.compile(r"^(.+?)型?の配列$")
_SIMPLE_TYPE_RE = re.compile(r"^(.+?)型$")


def _resolve_base_type(prefix: str) -> IPAType:
    """型名プレフィックスから IPAType を解決する"""
    for key, ipa_type in _TYPE_PREFIX_MAP.items():
        if prefix == key or prefix == key + "型":
            return ipa_type
    return IPAType.CUSTOM


def parse_type_annotation(raw: str) -> TypeInfo:
    """日本語の型注釈文字列をパースして TypeInfo を返す

    Args:
        raw: 型注釈文字列（例: "整数型", "整数型の配列", "整数型の二次元配列"）

    Returns:
        解析された TypeInfo

    Examples:
        >>> parse_type_annotation("整数型")
        TypeInfo(base_type=<IPAType.INTEGER: '整数型'>, raw='整数型')
        >>> parse_type_annotation("整数型の配列")
        TypeInfo(base_type=<IPAType.INTEGER: '整数型'>, is_array=True, raw='整数型の配列')
        >>> parse_type_annotation("ListElement")
        TypeInfo(base_type=<IPAType.CUSTOM: 'custom'>, class_name='ListElement', raw='ListElement')
    """
    raw = raw.strip()

    # 配列の配列: "整数型配列の配列"
    if m := _ARRAY_OF_ARRAYS_RE.match(raw):
        base = _resolve_base_type(m.group(1))
        class_name = m.group(1) if base == IPAType.CUSTOM else None
        return TypeInfo(
            base_type=base, is_array_of_arrays=True, class_name=class_name, raw=raw
        )

    # 二次元配列: "整数型の二次元配列"
    if m := _2D_ARRAY_RE.match(raw):
        base = _resolve_base_type(m.group(1))
        class_name = m.group(1) if base == IPAType.CUSTOM else None
        return TypeInfo(
            base_type=base, is_2d_array=True, class_name=class_name, raw=raw
        )

    # 一次元配列: "整数型の配列"
    if m := _ARRAY_RE.match(raw):
        base = _resolve_base_type(m.group(1))
        class_name = m.group(1) if base == IPAType.CUSTOM else None
        return TypeInfo(
            base_type=base, is_array=True, class_name=class_name, raw=raw
        )

    # 単純型: "整数型"
    if m := _SIMPLE_TYPE_RE.match(raw):
        base = _resolve_base_type(m.group(1))
        if base != IPAType.CUSTOM:
            return TypeInfo(base_type=base, raw=raw)
        # "〇〇型" だが既知の型ではない場合はカスタム型
        return TypeInfo(base_type=IPAType.CUSTOM, class_name=raw, raw=raw)

    # それ以外はカスタム型（クラス名: ListElement, PrioQueue 等）
    return TypeInfo(base_type=IPAType.CUSTOM, class_name=raw, raw=raw)
