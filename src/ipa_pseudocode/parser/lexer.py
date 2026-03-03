"""字句解析器（レクサー）

IPA擬似言語のソースコードをトークン列に変換する。
全角/半角文字の混在、日本語キーワード、Unicode演算子に対応。
"""

from __future__ import annotations

from .tokens import KEYWORDS, SYMBOL_OPERATORS, Token, TokenType


def tokenize(source: str) -> list[Token]:
    """ソースコード全体をトークン列に変換する

    Args:
        source: IPA擬似言語のソースコード

    Returns:
        トークンのリスト（末尾にEOFトークンを含む）
    """
    lexer = Lexer(source)
    return lexer.tokenize()


class Lexer:
    """IPA擬似言語の字句解析器"""

    def __init__(self, source: str) -> None:
        self._source = source
        self._pos = 0
        self._line = 1
        self._col = 1
        self._tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """ソースコード全体をトークン化する"""
        while self._pos < len(self._source):
            self._skip_whitespace()
            if self._pos >= len(self._source):
                break

            ch = self._source[self._pos]

            # 改行
            if ch == "\n":
                self._tokens.append(Token(TokenType.NEWLINE, "\n", self._line, self._col))
                self._advance()
                self._line += 1
                self._col = 1
                continue

            # コメント
            if self._try_comment():
                continue

            # 文字列リテラル
            if ch == '"' or ch == "\u201c" or ch == "\u201d":
                self._read_string_literal()
                continue

            # 数値リテラル
            if ch.isdigit():
                self._read_number()
                continue

            # 記号演算子
            if self._try_symbol_operator():
                continue

            # 識別子 or キーワード
            if self._is_ident_start(ch):
                self._read_identifier_or_keyword()
                continue

            # 不明な文字はスキップ
            self._advance()

        self._tokens.append(Token(TokenType.EOF, "", self._line, self._col))
        return self._tokens

    def _skip_whitespace(self) -> None:
        """空白文字（改行以外）をスキップする"""
        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch in (" ", "\t", "\u3000", "\r"):  # 半角スペース、タブ、全角スペース、CR
                self._advance()
            else:
                break

    def _advance(self) -> None:
        """1文字進める"""
        self._pos += 1
        self._col += 1

    def _peek(self, offset: int = 0) -> str:
        """現在位置から offset 先の文字を返す"""
        idx = self._pos + offset
        if idx < len(self._source):
            return self._source[idx]
        return ""

    def _try_comment(self) -> bool:
        """コメントを読み取る。成功時は True を返す"""
        # ブロックコメント: /* ... */
        if self._source[self._pos : self._pos + 2] == "/*":
            start_line = self._line
            start_col = self._col
            self._pos += 2
            self._col += 2
            comment_text = "/*"
            while self._pos < len(self._source):
                if self._source[self._pos : self._pos + 2] == "*/":
                    comment_text += "*/"
                    self._pos += 2
                    self._col += 2
                    break
                if self._source[self._pos] == "\n":
                    comment_text += "\n"
                    self._pos += 1
                    self._line += 1
                    self._col = 1
                else:
                    comment_text += self._source[self._pos]
                    self._advance()
            self._tokens.append(Token(TokenType.COMMENT, comment_text, start_line, start_col))
            return True

        # 行コメント: // ...
        if self._source[self._pos : self._pos + 2] == "//":
            start_line = self._line
            start_col = self._col
            comment_text = ""
            while self._pos < len(self._source) and self._source[self._pos] != "\n":
                comment_text += self._source[self._pos]
                self._advance()
            self._tokens.append(Token(TokenType.COMMENT, comment_text, start_line, start_col))
            return True

        return False

    def _read_string_literal(self) -> None:
        """文字列リテラルを読み取る: "..." or "..." """
        start_line = self._line
        start_col = self._col
        self._advance()  # 開始引用符をスキップ

        value = ""
        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch == '"' or ch == "\u201d":  # " or 右ダブルクォート
                self._advance()  # 終了引用符をスキップ
                break
            if ch == "\n":
                break  # 改行で強制終了
            value += ch
            self._advance()

        self._tokens.append(Token(TokenType.STRING_LITERAL, value, start_line, start_col))

    def _read_number(self) -> None:
        """数値リテラルを読み取る"""
        start_line = self._line
        start_col = self._col
        num_str = ""
        has_dot = False

        while self._pos < len(self._source):
            ch = self._source[self._pos]
            if ch.isdigit():
                num_str += ch
                self._advance()
            elif ch == "." and not has_dot:
                # 次の文字が数字なら小数点
                if self._peek(1).isdigit():
                    has_dot = True
                    num_str += ch
                    self._advance()
                else:
                    break
            else:
                break

        if has_dot:
            self._tokens.append(Token(TokenType.REAL_LITERAL, num_str, start_line, start_col))
        else:
            self._tokens.append(Token(TokenType.INTEGER_LITERAL, num_str, start_line, start_col))

    def _try_symbol_operator(self) -> bool:
        """記号演算子を読み取る。成功時は True を返す"""
        for symbol, token_type in SYMBOL_OPERATORS:
            if self._source[self._pos : self._pos + len(symbol)] == symbol:
                self._tokens.append(
                    Token(token_type, symbol, self._line, self._col)
                )
                self._pos += len(symbol)
                self._col += len(symbol)
                return True
        return False

    def _is_ident_start(self, ch: str) -> bool:
        """識別子の先頭文字として有効かどうか"""
        if ch.isalpha() or ch == "_":
            return True
        # 日本語文字（漢字、ひらがな、カタカナ）
        cp = ord(ch)
        if 0x3040 <= cp <= 0x309F:  # ひらがな
            return True
        if 0x30A0 <= cp <= 0x30FF:  # カタカナ
            # ー (U+30FC) はマイナス記号として使用されるため除外
            if cp == 0x30FC:
                return False
            return True
        if 0x4E00 <= cp <= 0x9FFF:  # CJK統合漢字
            return True
        return False

    def _is_ident_char(self, ch: str) -> bool:
        """識別子の構成文字として有効かどうか"""
        return self._is_ident_start(ch) or ch.isdigit()

    def _read_identifier_or_keyword(self) -> None:
        """識別子またはキーワードを読み取る"""
        start_line = self._line
        start_col = self._col
        ident = ""

        while self._pos < len(self._source) and self._is_ident_char(self._source[self._pos]):
            ident += self._source[self._pos]
            self._advance()

        # キーワード判定（大文字小文字を区別しない）
        lower = ident.lower()
        if lower in KEYWORDS:
            self._tokens.append(Token(KEYWORDS[lower], ident, start_line, start_col))
        else:
            self._tokens.append(Token(TokenType.IDENTIFIER, ident, start_line, start_col))
