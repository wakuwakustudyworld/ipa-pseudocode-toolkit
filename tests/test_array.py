"""Array / Array2D クラスのテスト"""

import pytest

from ipa_pseudocode.core.array import Array, Array2D


class TestArray:
    """1-based配列のテスト"""

    def test_create_empty(self):
        arr = Array(0)
        assert len(arr) == 0

    def test_create_with_size(self):
        arr = Array(3)
        assert len(arr) == 3

    def test_create_with_init_value(self):
        arr = Array(3, init=0)
        assert arr[1] == 0
        assert arr[2] == 0
        assert arr[3] == 0

    def test_from_literal(self):
        arr = Array.from_literal([11, 12, 13, 14, 15])
        assert len(arr) == 5
        assert arr[1] == 11
        assert arr[4] == 14
        assert arr[5] == 15

    def test_setitem_getitem(self):
        arr = Array(3)
        arr[1] = 10
        arr[2] = 20
        arr[3] = 30
        assert arr[1] == 10
        assert arr[2] == 20
        assert arr[3] == 30

    def test_index_out_of_range_low(self):
        arr = Array(3)
        with pytest.raises(IndexError, match="添字が範囲外"):
            _ = arr[0]

    def test_index_out_of_range_high(self):
        arr = Array(3)
        with pytest.raises(IndexError, match="添字が範囲外"):
            _ = arr[4]

    def test_append(self):
        arr = Array(2, init=0)
        arr.append(99)
        assert len(arr) == 3
        assert arr[3] == 99

    def test_iter(self):
        arr = Array.from_literal([10, 20, 30])
        assert list(arr) == [10, 20, 30]

    def test_to_list(self):
        arr = Array.from_literal([1, 2, 3])
        assert arr.to_list() == [1, 2, 3]

    def test_eq(self):
        a = Array.from_literal([1, 2, 3])
        b = Array.from_literal([1, 2, 3])
        c = Array.from_literal([1, 2, 4])
        assert a == b
        assert a != c

    def test_repr(self):
        arr = Array.from_literal([1, 2])
        assert repr(arr) == "Array([1, 2])"


class TestArray2D:
    """1-based二次元配列のテスト"""

    def test_create(self):
        arr = Array2D(2, 3, init=0)
        assert arr.rows == 2
        assert arr.cols == 3

    def test_setitem_getitem(self):
        arr = Array2D(2, 3, init=0)
        arr[1, 2] = 42
        assert arr[1, 2] == 42
        assert arr[1, 1] == 0

    def test_from_literal(self):
        arr = Array2D.from_literal([[11, 12, 13], [21, 22, 23]])
        assert arr[1, 1] == 11
        assert arr[1, 3] == 13
        assert arr[2, 3] == 23

    def test_row(self):
        arr = Array2D.from_literal([[1, 2], [3, 4]])
        assert arr.row(1) == [1, 2]
        assert arr.row(2) == [3, 4]

    def test_col(self):
        arr = Array2D.from_literal([[1, 2], [3, 4]])
        assert arr.col(1) == [1, 3]
        assert arr.col(2) == [2, 4]

    def test_index_out_of_range(self):
        arr = Array2D(2, 3)
        with pytest.raises(IndexError, match="行番号が範囲外"):
            _ = arr[0, 1]
        with pytest.raises(IndexError, match="列番号が範囲外"):
            _ = arr[1, 0]
        with pytest.raises(IndexError, match="行番号が範囲外"):
            _ = arr[3, 1]

    def test_single_index_returns_row(self):
        arr = Array2D.from_literal([[10, 20], [30, 40]])
        assert arr[1] == [10, 20]

    def test_eq(self):
        a = Array2D.from_literal([[1, 2], [3, 4]])
        b = Array2D.from_literal([[1, 2], [3, 4]])
        c = Array2D.from_literal([[1, 2], [3, 5]])
        assert a == b
        assert a != c

    def test_from_literal_empty(self):
        arr = Array2D.from_literal([])
        assert arr.rows == 0
        assert arr.cols == 0
