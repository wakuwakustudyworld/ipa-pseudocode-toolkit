"""トークン定義

IPA擬似言語の字句解析で使用するトークン型とトークンデータクラスを定義する。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """トークンの種類"""

    # --- リテラル ---
    INTEGER_LITERAL = auto()
    REAL_LITERAL = auto()
    STRING_LITERAL = auto()

    # --- 識別子 ---
    IDENTIFIER = auto()

    # --- 制御キーワード ---
    IF = auto()
    ELSEIF = auto()
    ELSE = auto()
    ENDIF = auto()
    WHILE = auto()
    ENDWHILE = auto()
    DO = auto()
    FOR = auto()
    ENDFOR = auto()
    RETURN = auto()

    # --- 論理・ブール ---
    TRUE = auto()
    FALSE = auto()
    NOT = auto()
    AND = auto()
    OR = auto()

    # --- 算術キーワード ---
    MOD = auto()

    # --- 宣言マーカー ---
    CIRCLE = auto()  # ○

    # --- 代入 ---
    ASSIGN = auto()  # ←

    # --- 算術演算子 ---
    PLUS = auto()  # ＋ or +
    MINUS = auto()  # − or - (各種Unicode)
    MULTIPLY = auto()  # ×
    DIVIDE = auto()  # ÷

    # --- 関係演算子 ---
    EQUAL = auto()  # ＝ or =
    NOT_EQUAL = auto()  # ≠
    LESS_THAN = auto()  # ＜ or <
    GREATER_THAN = auto()  # ＞ or >
    LESS_EQUAL = auto()  # ≦
    GREATER_EQUAL = auto()  # ≧

    # --- ビット演算子 ---
    BIT_AND = auto()  # ∧
    BIT_OR = auto()  # ∨
    SHIFT_LEFT = auto()  # <<
    SHIFT_RIGHT = auto()  # >>

    # --- 区切り ---
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # , or ，
    COLON = auto()  # : or ：
    DOT = auto()  # .

    # --- 特殊 ---
    NEWLINE = auto()
    COMMENT = auto()
    EOF = auto()


# 英字キーワードの対応表
KEYWORDS: dict[str, TokenType] = {
    "if": TokenType.IF,
    "elseif": TokenType.ELSEIF,
    "else": TokenType.ELSE,
    "endif": TokenType.ENDIF,
    "while": TokenType.WHILE,
    "endwhile": TokenType.ENDWHILE,
    "do": TokenType.DO,
    "for": TokenType.FOR,
    "endfor": TokenType.ENDFOR,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "not": TokenType.NOT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "mod": TokenType.MOD,
}

# 記号演算子の対応表（長いものから順にマッチ）
SYMBOL_OPERATORS: list[tuple[str, TokenType]] = [
    # 複数文字
    ("<<", TokenType.SHIFT_LEFT),
    (">>", TokenType.SHIFT_RIGHT),
    # 全角演算子
    ("←", TokenType.ASSIGN),
    ("≦", TokenType.LESS_EQUAL),
    ("≧", TokenType.GREATER_EQUAL),
    ("≠", TokenType.NOT_EQUAL),
    ("＝", TokenType.EQUAL),
    ("＜", TokenType.LESS_THAN),
    ("＞", TokenType.GREATER_THAN),
    ("＋", TokenType.PLUS),
    ("－", TokenType.MINUS),  # U+FF0D (Fullwidth Hyphen-Minus)
    ("−", TokenType.MINUS),  # U+2212 (Minus Sign)
    ("ー", TokenType.MINUS),  # U+30FC (Katakana Prolonged Sound Mark, often used as minus)
    ("×", TokenType.MULTIPLY),
    ("÷", TokenType.DIVIDE),
    ("∧", TokenType.BIT_AND),
    ("∨", TokenType.BIT_OR),
    ("○", TokenType.CIRCLE),
    ("，", TokenType.COMMA),
    ("：", TokenType.COLON),
    # 半角演算子
    ("=", TokenType.EQUAL),
    ("<", TokenType.LESS_THAN),
    (">", TokenType.GREATER_THAN),
    ("+", TokenType.PLUS),
    ("-", TokenType.MINUS),
    # 区切り
    ("(", TokenType.LPAREN),
    (")", TokenType.RPAREN),
    ("[", TokenType.LBRACKET),
    ("]", TokenType.RBRACKET),
    ("{", TokenType.LBRACE),
    ("}", TokenType.RBRACE),
    (",", TokenType.COMMA),
    (":", TokenType.COLON),
    (".", TokenType.DOT),
]


@dataclass(frozen=True)
class Token:
    """レクサーが生成するトークン"""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.column})"
