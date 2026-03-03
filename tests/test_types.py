"""型定義のテスト"""

from ipa_pseudocode.core.types import IPAType, TypeInfo, parse_type_annotation


class TestParseTypeAnnotation:
    def test_integer(self):
        info = parse_type_annotation("整数型")
        assert info.base_type == IPAType.INTEGER
        assert not info.is_array
        assert not info.is_2d_array

    def test_real(self):
        info = parse_type_annotation("実数型")
        assert info.base_type == IPAType.REAL

    def test_string(self):
        info = parse_type_annotation("文字列型")
        assert info.base_type == IPAType.STRING

    def test_char(self):
        info = parse_type_annotation("文字型")
        assert info.base_type == IPAType.CHAR

    def test_boolean(self):
        info = parse_type_annotation("論理型")
        assert info.base_type == IPAType.BOOLEAN

    def test_integer_array(self):
        info = parse_type_annotation("整数型の配列")
        assert info.base_type == IPAType.INTEGER
        assert info.is_array

    def test_integer_2d_array(self):
        info = parse_type_annotation("整数型の二次元配列")
        assert info.base_type == IPAType.INTEGER
        assert info.is_2d_array

    def test_custom_type(self):
        info = parse_type_annotation("ListElement")
        assert info.base_type == IPAType.CUSTOM
        assert info.class_name == "ListElement"

    def test_custom_array(self):
        info = parse_type_annotation("ListElementの配列")
        assert info.base_type == IPAType.CUSTOM
        assert info.is_array
        assert info.class_name == "ListElement"

    def test_array_of_arrays(self):
        info = parse_type_annotation("整数型配列の配列")
        assert info.base_type == IPAType.INTEGER
        assert info.is_array_of_arrays

    def test_raw_preserved(self):
        info = parse_type_annotation("整数型")
        assert info.raw == "整数型"


class TestTypeInfoPythonHint:
    def test_integer(self):
        info = TypeInfo(base_type=IPAType.INTEGER)
        assert info.python_type_hint == "int"

    def test_array(self):
        info = TypeInfo(base_type=IPAType.INTEGER, is_array=True)
        assert info.python_type_hint == "list[int]"

    def test_2d_array(self):
        info = TypeInfo(base_type=IPAType.REAL, is_2d_array=True)
        assert info.python_type_hint == "list[list[float]]"

    def test_custom(self):
        info = TypeInfo(base_type=IPAType.CUSTOM, class_name="Node")
        assert info.python_type_hint == "Node"
