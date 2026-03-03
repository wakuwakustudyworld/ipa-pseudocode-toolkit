"""中核データ構造（型定義・配列・文字列操作）"""

from .array import Array, Array2D
from .types import IPAType, TypeInfo, parse_type_annotation

__all__ = ["Array", "Array2D", "IPAType", "TypeInfo", "parse_type_annotation"]
