"""IPA擬似言語の文字列操作ヘルパー

擬似言語の文字列操作（1-based文字アクセス等）をPythonで実現するユーティリティ。
"""


def char_at(s: str, pos: int) -> str:
    """1-basedで文字列の指定位置の文字を返す

    擬似言語の「binaryのi文字目の文字」に対応。

    Args:
        s: 文字列
        pos: 位置（1始まり）

    Returns:
        指定位置の文字

    Raises:
        IndexError: 位置が範囲外の場合
    """
    if not (1 <= pos <= len(s)):
        raise IndexError(
            f"文字位置が範囲外です: {pos}（有効範囲: 1〜{len(s)}）"
        )
    return s[pos - 1]


def str_length(s: str) -> int:
    """文字列の文字数を返す

    擬似言語の「binaryの文字数」に対応。
    """
    return len(s)
