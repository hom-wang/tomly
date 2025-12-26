"""
Nested path operations tests for DataDict.
Tests get_nested, set_nested, delete_nested, and path manipulation.
"""

import pytest

from tomly import DataDict

# ==============================================================
# Test get_nested() method.
# ==============================================================


def test_get_simple_path():
    """Test retrieving a simple nested value."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    assert dd.get_nested("a.b.c") == 1


def test_get_with_default_on_missing():
    """Test default value returned when path doesn't exist."""
    dd = DataDict({"a": {"b": 1}})
    assert dd.get_nested("a.x.y", default="missing") == "missing"


def test_get_with_none_default():
    """Test that None is returned by default for missing paths."""
    dd = DataDict({"a": 1})
    assert dd.get_nested("x.y.z") is None


def test_get_root_with_empty_path():
    """Test that empty path returns the DataDict itself."""
    dd = DataDict({"a": 1})
    result = dd.get_nested("")
    assert result is dd


def test_get_with_list_path():
    """Test get_nested with list of keys instead of string."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    assert dd.get_nested(["a", "b", "c"]) == 1


def test_get_single_level():
    """Test get_nested with single level path."""
    dd = DataDict({"key": "value"})
    assert dd.get_nested("key") == "value"


def test_get_nonexistent_single_key():
    """Test get_nested with non-existent single key."""
    dd = DataDict({"a": 1})
    assert dd.get_nested("b", default="nope") == "nope"


def test_get_through_non_dict_value():
    """Test get_nested returns default when path goes through non-dict."""
    dd = DataDict({"a": 123})
    assert dd.get_nested("a.b.c", default="error") == "error"


def test_get_custom_separator():
    """Test get_nested with custom separator."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    assert dd.get_nested("a/b/c", separator="/") == 1


def test_get_path_with_special_characters_in_keys():
    """Test get_nested with keys containing dots."""
    dd = DataDict({"a.b": {"c": 1}})
    # Note: This uses list path to handle dots in keys
    assert dd.get_nested(["a.b", "c"]) == 1


def test_get_deeply_nested():
    """Test get_nested with very deep nesting."""
    dd = DataDict({"l1": {"l2": {"l3": {"l4": {"l5": {"l6": {"value": "deep"}}}}}}})
    assert dd.get_nested("l1.l2.l3.l4.l5.l6.value") == "deep"


def test_get_returns_nested_datadict():
    """Test that get_nested can return nested DataDict objects."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    result = dd.get_nested("a.b")
    assert isinstance(result, DataDict)
    assert result.c == 1


# ==============================================================
# Test set_nested() method.
# ==============================================================


def test_set_creates_intermediate_dicts():
    """Test that set_nested auto-creates intermediate dictionaries."""
    dd = DataDict()
    dd.set_nested("a.b.c", 123)
    assert dd.a.b.c == 123
    assert isinstance(dd.a, DataDict)
    assert isinstance(dd.a.b, DataDict)


def test_set_overwrites_existing_value():
    """Test that set_nested overwrites existing values."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    dd.set_nested("a.b.c", 999)
    assert dd.a.b.c == 999


def test_set_with_list_path():
    """Test set_nested with list of keys."""
    dd = DataDict()
    dd.set_nested(["x", "y", "z"], "value")
    assert dd.x.y.z == "value"


def test_set_single_level():
    """Test set_nested with single level path."""
    dd = DataDict()
    dd.set_nested("key", "value")
    assert dd.key == "value"


def test_set_overwrites_non_dict_intermediate():
    """Test that set_nested overwrites non-dict intermediate values."""
    dd = DataDict({"a": 123})  # 'a' is an int
    dd.set_nested("a.b.c", "new")
    assert dd.a.b.c == "new"
    assert isinstance(dd.a, DataDict)


def test_set_custom_separator():
    """Test set_nested with custom separator."""
    dd = DataDict()
    dd.set_nested("a/b/c", 1, separator="/")
    assert dd.a.b.c == 1


def test_set_empty_path_raises_error():
    """Test that set_nested with empty path raises ValueError."""
    dd = DataDict()
    with pytest.raises(ValueError, match="Path must not be empty"):
        dd.set_nested("", 1)


def test_set_empty_list_path_raises_error():
    """Test that set_nested with empty list raises ValueError."""
    dd = DataDict()
    with pytest.raises(ValueError, match="Path must not be empty"):
        dd.set_nested([], 1)


def test_set_wraps_dict_values():
    """Test that set_nested wraps dict values into DataDict."""
    dd = DataDict()
    dd.set_nested("a.b", {"c": 1, "d": 2})
    assert isinstance(dd.a.b, DataDict)
    assert dd.a.b.c == 1


def test_set_deeply_nested():
    """Test set_nested with very deep paths."""
    dd = DataDict()
    dd.set_nested("l1.l2.l3.l4.l5.l6.value", "deep")
    assert dd.l1.l2.l3.l4.l5.l6.value == "deep"


def test_set_multiple_paths():
    """Test setting multiple nested paths in succession."""
    dd = DataDict()
    dd.set_nested("config.db.host", "localhost")
    dd.set_nested("config.db.port", 5432)
    dd.set_nested("config.cache.host", "redis")

    assert dd.config.db.host == "localhost"
    assert dd.config.db.port == 5432
    assert dd.config.cache.host == "redis"


def test_set_preserves_siblings():
    """Test that set_nested preserves sibling values."""
    dd = DataDict({"a": {"b": 1, "c": 2}})
    dd.set_nested("a.d", 3)
    assert dd.a.b == 1
    assert dd.a.c == 2
    assert dd.a.d == 3


def test_set_on_frozen_raises_error():
    """Test that set_nested on frozen DataDict raises error."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="frozen"):
        dd.set_nested("b.c", 2)


# ==============================================================
# Test delete_nested() method.
# ==============================================================


def test_delete_existing_path():
    """Test deleting an existing nested path."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    result = dd.delete_nested("a.b.c")
    assert result is True
    assert "c" not in dd.a.b


def test_delete_nonexistent_path():
    """Test deleting a non-existent path returns False."""
    dd = DataDict({"a": {"b": 1}})
    result = dd.delete_nested("a.x.y")
    assert result is False


def test_delete_with_list_path():
    """Test delete_nested with list of keys."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    result = dd.delete_nested(["a", "b", "c"])
    assert result is True
    assert "c" not in dd.a.b


def test_delete_single_level():
    """Test delete_nested with single level path."""
    dd = DataDict({"key": "value", "other": 123})
    result = dd.delete_nested("key")
    assert result is True
    assert "key" not in dd
    assert dd.other == 123


def test_delete_empty_path():
    """Test that delete_nested with empty path returns False."""
    dd = DataDict({"a": 1})
    result = dd.delete_nested("")
    assert result is False


def test_delete_custom_separator():
    """Test delete_nested with custom separator."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    result = dd.delete_nested("a/b/c", separator="/")
    assert result is True
    assert "c" not in dd.a.b


def test_delete_through_non_dict():
    """Test delete_nested returns False when path goes through non-dict."""
    dd = DataDict({"a": 123})
    result = dd.delete_nested("a.b.c")
    assert result is False


def test_delete_preserves_siblings():
    """Test that delete_nested preserves sibling values."""
    dd = DataDict({"a": {"b": 1, "c": 2, "d": 3}})
    dd.delete_nested("a.b")
    assert "b" not in dd.a
    assert dd.a.c == 2
    assert dd.a.d == 3


def test_delete_intermediate_becomes_empty():
    """Test that intermediate dicts remain even if empty after deletion."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    dd.delete_nested("a.b.c")
    assert "c" not in dd.a.b
    assert "b" in dd.a  # Empty dict remains
    assert len(dd.a.b) == 0


def test_delete_on_frozen_raises_error():
    """Test that delete_nested on frozen DataDict raises error."""
    dd = DataDict({"a": {"b": 1}}).freeze()
    with pytest.raises(TypeError, match="frozen"):
        dd.delete_nested("a.b")


# ==============================================================
# Test edge cases for nested path operations.
# ==============================================================


def test_numeric_string_keys():
    """Test paths with numeric string keys."""
    dd = DataDict({"1": {"2": {"3": "value"}}})
    assert dd.get_nested("1.2.3") == "value"

    dd.set_nested("4.5.6", "new")
    assert dd["4"]["5"]["6"] == "new"


def test_keys_with_underscores():
    """Test paths with underscored keys."""
    dd = DataDict()
    dd.set_nested("my_config.db_settings.max_connections", 100)
    assert dd.my_config.db_settings.max_connections == 100


def test_mixed_access_patterns():
    """Test mixing path operations with direct access."""
    dd = DataDict()
    dd.set_nested("a.b.c", 1)
    dd.a.b.d = 2  # Direct attribute assignment
    dd["a"]["b"]["e"] = 3  # Dict-style assignment

    assert dd.get_nested("a.b.c") == 1
    assert dd.get_nested("a.b.d") == 2
    assert dd.get_nested("a.b.e") == 3


def test_overwriting_path_types():
    """Test overwriting values with different types."""
    dd = DataDict({"a": {"b": 123}})

    # Overwrite int with dict
    dd.set_nested("a.b.c", "new")
    assert dd.a.b.c == "new"

    # Overwrite dict with scalar
    dd.set_nested("a.b", 456)
    assert dd.a.b == 456


def test_very_long_paths():
    """Test operations with very long paths."""
    # Create a 20-level deep path
    keys = [f"level{i}" for i in range(20)]
    path = ".".join(keys)

    dd = DataDict()
    dd.set_nested(path, "deep_value")
    assert dd.get_nested(path) == "deep_value"

    result = dd.delete_nested(path)
    assert result is True
    assert dd.get_nested(path) is None


def test_path_with_none_values():
    """Test path operations with None values."""
    dd = DataDict({"a": {"b": None}})

    # Can get None value
    assert dd.get_nested("a.b") is None

    # Can set through None value (overwrites it)
    dd.set_nested("a.b.c", 1)
    assert dd.a.b.c == 1


def test_concurrent_path_modifications():
    """Test multiple path modifications don't interfere."""
    dd = DataDict()

    # Set multiple independent paths
    dd.set_nested("path1.a.b", 1)
    dd.set_nested("path2.a.b", 2)
    dd.set_nested("path3.a.b", 3)

    assert dd.path1.a.b == 1
    assert dd.path2.a.b == 2
    assert dd.path3.a.b == 3

    # Delete one shouldn't affect others
    dd.delete_nested("path2.a.b")
    assert dd.path1.a.b == 1
    assert dd.path3.a.b == 3
