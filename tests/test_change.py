import numpy as np
import pytest
from mfca.change import detect_change

def test_detect_change_simple():
    class_a = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    class_b = np.array([[0, 0], [1, 1]], dtype=np.uint8)
    expected = np.array([[0, 1], [0, 1]], dtype=np.uint8)
    result = detect_change(class_a, class_b, None)
    np.testing.assert_array_equal(result, expected)

def test_detect_change_mismatch_shape():
    class_a = np.zeros((2, 2), dtype=np.uint8)
    class_b = np.zeros((3, 2), dtype=np.uint8)
    with pytest.raises(ValueError):
        detect_change(class_a, class_b, None)
