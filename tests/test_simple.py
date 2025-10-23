"""
Simple tests that don't require full app dependencies
"""
import pytest


def test_basic_math():
    """Test basic functionality"""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations"""
    text = "Hello, World!"
    assert len(text) == 13
    assert "Hello" in text


def test_list_operations():
    """Test list operations"""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15


def test_dictionary_operations():
    """Test dictionary operations"""
    data = {"name": "test", "value": 42}
    assert data["name"] == "test"
    assert data["value"] == 42
    assert len(data) == 2


class TestBasicFunctionality:
    """Test class for basic functionality"""
    
    def test_class_method(self):
        """Test class method"""
        assert True
    
    def test_another_class_method(self):
        """Test another class method"""
        result = 2 * 3
        assert result == 6
