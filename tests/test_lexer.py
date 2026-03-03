"""字句解析器のテスト"""

from ipa_pseudocode.parser.lexer import tokenize
from ipa_pseudocode.parser.tokens import TokenType


def _types(tokens):
    """EOFを除くトークンの型リストを返す"""
    return [t.type for t in tokens if t.type != TokenType.EOF]


def _values(tokens):
    """EOF/NEWLINEを除くトークンの値リストを返す"""
    return [t.value for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]


class TestLiterals:
    def test_integer(self):
        tokens = tokenize("42")
        assert tokens[0].type == TokenType.INTEGER_LITERAL
        assert tokens[0].value == "42"

    def test_real(self):
        tokens = tokenize("3.14")
        assert tokens[0].type == TokenType.REAL_LITERAL
        assert tokens[0].value == "3.14"

    def test_string_literal(self):
        tokens = tokenize('"hello"')
        assert tokens[0].type == TokenType.STRING_LITERAL
        assert tokens[0].value == "hello"

    def test_unicode_string_literal(self):
        tokens = tokenize('\u201chello\u201d')
        assert tokens[0].type == TokenType.STRING_LITERAL
        assert tokens[0].value == "hello"


class TestKeywords:
    def test_control_keywords(self):
        for kw in ["if", "else", "elseif", "endif", "while", "endwhile", "for", "endfor"]:
            tokens = tokenize(kw)
            assert tokens[0].type.name == kw.upper()

    def test_boolean_keywords(self):
        tokens = tokenize("true false")
        types = _types(tokens)
        assert TokenType.TRUE in types
        assert TokenType.FALSE in types

    def test_logic_keywords(self):
        tokens = tokenize("not and or")
        types = _types(tokens)
        assert TokenType.NOT in types
        assert TokenType.AND in types
        assert TokenType.OR in types

    def test_case_insensitive(self):
        tokens = tokenize("IF ELSE RETURN")
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.ELSE
        assert tokens[2].type == TokenType.RETURN


class TestOperators:
    def test_assign(self):
        tokens = tokenize("x ← 10")
        types = _types(tokens)
        assert TokenType.ASSIGN in types

    def test_fullwidth_arithmetic(self):
        tokens = tokenize("a ＋ b − c × d ÷ e")
        types = _types(tokens)
        assert TokenType.PLUS in types
        assert TokenType.MINUS in types
        assert TokenType.MULTIPLY in types
        assert TokenType.DIVIDE in types

    def test_comparison(self):
        tokens = tokenize("a ≠ b")
        types = _types(tokens)
        assert TokenType.NOT_EQUAL in types

    def test_less_greater_equal(self):
        tokens = tokenize("a ≦ b ≧ c")
        types = _types(tokens)
        assert TokenType.LESS_EQUAL in types
        assert TokenType.GREATER_EQUAL in types

    def test_halfwidth_operators(self):
        tokens = tokenize("a + b - c")
        types = _types(tokens)
        assert TokenType.PLUS in types
        assert TokenType.MINUS in types

    def test_circle_marker(self):
        tokens = tokenize("○整数型")
        assert tokens[0].type == TokenType.CIRCLE

    def test_bit_operators(self):
        tokens = tokenize("a ∧ b ∨ c")
        types = _types(tokens)
        assert TokenType.BIT_AND in types
        assert TokenType.BIT_OR in types

    def test_shift_operators(self):
        tokens = tokenize("a << 2 >> 1")
        types = _types(tokens)
        assert TokenType.SHIFT_LEFT in types
        assert TokenType.SHIFT_RIGHT in types


class TestDelimiters:
    def test_parens(self):
        tokens = tokenize("(a)")
        types = _types(tokens)
        assert TokenType.LPAREN in types
        assert TokenType.RPAREN in types

    def test_brackets(self):
        tokens = tokenize("a[1]")
        types = _types(tokens)
        assert TokenType.LBRACKET in types
        assert TokenType.RBRACKET in types

    def test_braces(self):
        tokens = tokenize("{1, 2}")
        types = _types(tokens)
        assert TokenType.LBRACE in types
        assert TokenType.RBRACE in types
        assert TokenType.COMMA in types

    def test_fullwidth_comma_colon(self):
        tokens = tokenize("整数型：x，y")
        types = _types(tokens)
        assert TokenType.COLON in types
        assert TokenType.COMMA in types


class TestComments:
    def test_line_comment(self):
        tokens = tokenize("x ← 1 // comment")
        types = _types(tokens)
        assert TokenType.COMMENT in types

    def test_block_comment(self):
        tokens = tokenize("x ← /* comment */ 1")
        types = _types(tokens)
        assert TokenType.COMMENT in types


class TestIdentifiers:
    def test_ascii_identifier(self):
        tokens = tokenize("myVar")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "myVar"

    def test_japanese_identifier(self):
        tokens = tokenize("年齢")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "年齢"

    def test_mixed_identifier(self):
        tokens = tokenize("pnList")
        assert tokens[0].type == TokenType.IDENTIFIER


class TestLineInfo:
    def test_line_column(self):
        tokens = tokenize("x ← 1\ny ← 2")
        # x should be line 1, y should be line 2
        x_tok = tokens[0]
        assert x_tok.line == 1
        assert x_tok.column == 1
