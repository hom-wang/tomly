"""
Conversion and utility method tests for DataDict.
Tests to_dict, flatten, merge, and other utility methods.
"""

import pytest

from tomly import DataDict

# ==============================================================
# Test to_dict() method for unwrapping DataDicts.
# ==============================================================


def test_simple_conversion():
    """Test converting simple DataDict to regular dict."""
    dd = DataDict({"a": 1, "b": 2})
    result = dd.to_dict()

    assert isinstance(result, dict)
    assert not isinstance(result, DataDict)
    assert result == {"a": 1, "b": 2}


def test_nested_conversion():
    """Test that nested DataDicts are also converted."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    result = dd.to_dict()

    assert isinstance(result, dict)
    assert isinstance(result["a"], dict)
    assert not isinstance(result["a"], DataDict)
    assert isinstance(result["a"]["b"], dict)
    assert not isinstance(result["a"]["b"], DataDict)


def test_list_with_datadicts_conversion():
    """Test converting lists containing DataDicts."""
    dd = DataDict(
        {
            "items": [
                {"id": 1, "name": "first"},
                {"id": 2, "name": "second"},
            ]
        }
    )
    result = dd.to_dict()

    assert isinstance(result["items"], list)
    assert isinstance(result["items"][0], dict)
    assert not isinstance(result["items"][0], DataDict)
    assert result["items"][0] == {"id": 1, "name": "first"}


def test_empty_datadict_conversion():
    """Test converting empty DataDict."""
    dd = DataDict()
    result = dd.to_dict()
    assert result == {}
    assert isinstance(result, dict)


def test_mixed_types_preservation():
    """Test that non-dict types are preserved during conversion."""
    dd = DataDict(
        {
            "int": 42,
            "float": 3.14,
            "str": "text",
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }
    )
    result = dd.to_dict()

    assert result["int"] == 42
    assert result["float"] == 3.14
    assert result["str"] == "text"
    assert result["bool"] is True
    assert result["none"] is None
    assert result["list"] == [1, 2, 3]
    assert isinstance(result["nested"], dict)


def test_deeply_nested_conversion():
    """Test conversion of deeply nested structures."""
    dd = DataDict({"l1": {"l2": {"l3": {"l4": {"l5": {"value": "deep"}}}}}})
    result = dd.to_dict()

    current = result
    for level in ["l1", "l2", "l3", "l4", "l5"]:
        assert isinstance(current[level], dict)
        assert not isinstance(current[level], DataDict)
        current = current[level]
    assert current["value"] == "deep"


def test_conversion_creates_new_dict():
    """Test that to_dict() creates a new dict, not a reference."""
    dd = DataDict({"a": {"b": 1}})
    result = dd.to_dict()

    # Modifying result should not affect original
    result["a"]["b"] = 999
    assert dd.a.b == 1  # Original unchanged


# ==============================================================
# Test flatten() method.
# ==============================================================


def test_simple_flatten():
    """Test flattening a simple nested structure."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    flat = dd.flatten()
    assert flat == {
        "a.b.c": 1,
    }


def test_flatten_multiple_branches():
    """Test flattening structure with multiple branches."""
    dd = DataDict(
        {
            "server": {"host": "localhost", "port": 8080},
            "database": {"host": "dbhost", "port": 5432},
        }
    )
    flat = dd.flatten()
    assert flat == {
        "server.host": "localhost",
        "server.port": 8080,
        "database.host": "dbhost",
        "database.port": 5432,
    }


def test_flatten_custom_separator():
    """Test flatten with custom separator."""
    dd = DataDict({"a": {"b": {"c": 1}}})
    flat = dd.flatten(separator="__")
    assert flat == {
        "a__b__c": 1,
    }


def test_flatten_with_parent_key():
    """Test flatten with parent key prefix."""
    dd = DataDict({"a": {"b": 1}})
    flat = dd.flatten(parent_key="root")
    assert flat == {
        "root.a.b": 1,
    }


def test_flatten_empty_datadict():
    """Test flattening empty DataDict."""
    dd = DataDict()
    flat = dd.flatten()
    assert flat == {}


def test_flatten_single_level():
    """Test flattening single-level structure."""
    dd = DataDict({"a": 1, "b": 2, "c": 3})
    flat = dd.flatten()
    assert flat == {"a": 1, "b": 2, "c": 3}


def test_flatten_without_list_expansion():
    """Test flatten with lists not expanded (default)."""
    dd = DataDict({"items": [1, 2, 3]})
    flat = dd.flatten(expand_lists=False)
    assert flat == {
        "items": [1, 2, 3],
    }


def test_flatten_with_list_expansion():
    """Test flatten with list expansion enabled."""
    dd = DataDict({"items": [1, 2, 3]})
    flat = dd.flatten(
        expand_lists=True,
    )
    assert flat == {
        "items[0]": 1,
        "items[1]": 2,
        "items[2]": 3,
    }


def test_flatten_nested_lists():
    """Test flatten with nested lists."""
    dd = DataDict(
        {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        }
    )
    flat = dd.flatten(expand_lists=True)
    assert flat == {
        "users[0].name": "Alice",
        "users[0].age": 30,
        "users[1].name": "Bob",
        "users[1].age": 25,
    }


def test_flatten_list_of_lists():
    """Test flatten with list of lists."""
    dd = DataDict({"matrix": [[1, 2], [3, 4]]})
    flat = dd.flatten(expand_lists=True)
    assert flat == {
        "matrix[0][0]": 1,
        "matrix[0][1]": 2,
        "matrix[1][0]": 3,
        "matrix[1][1]": 4,
    }


def test_flatten_empty_list():
    """Test flatten with empty list."""
    dd = DataDict(
        {
            "empty": [],
            "other": 1,
        }
    )
    flat = dd.flatten(expand_lists=True)
    assert flat == {
        "empty": [],
        "other": 1,
    }


def test_flatten_mixed_nesting():
    """Test flatten with mixed dict and list nesting."""
    dd = DataDict(
        {
            "config": {
                "servers": [
                    {"host": "server1", "port": 8001},
                    {"host": "server2", "port": 8002},
                ],
                "timeout": 30,
            }
        }
    )
    flat = dd.flatten(expand_lists=True)
    assert flat == {
        "config.servers[0].host": "server1",
        "config.servers[0].port": 8001,
        "config.servers[1].host": "server2",
        "config.servers[1].port": 8002,
        "config.timeout": 30,
    }


def test_flatten_deeply_nested():
    """Test flatten with very deep nesting."""
    dd = DataDict({"l1": {"l2": {"l3": {"l4": {"l5": {"value": "deep"}}}}}})
    flat = dd.flatten()
    assert flat == {
        "l1.l2.l3.l4.l5.value": "deep",
    }


def test_flatten_preserves_value_types():
    """Test that flatten preserves value types."""
    dd = DataDict(
        {
            "int": 42,
            "float": 3.14,
            "str": "text",
            "bool": True,
            "none": None,
        }
    )
    flat = dd.flatten()
    assert flat["int"] == 42
    assert flat["float"] == 3.14
    assert flat["str"] == "text"
    assert flat["bool"] is True
    assert flat["none"] is None


# ==============================================================
# Test merge() method.
# ==============================================================


def test_simple_merge():
    """Test merging a simple dict."""
    dd = DataDict({"a": 1, "b": 2})
    dd.merge({"c": 3})
    assert dd.a == 1
    assert dd.b == 2
    assert dd.c == 3


def test_merge_overwrites_scalars():
    """Test that merge overwrites scalar values."""
    dd = DataDict({"a": 1, "b": 2})
    dd.merge({"a": 10})
    assert dd.a == 10
    assert dd.b == 2


def test_merge_nested_dicts():
    """Test that merge recursively merges nested dicts."""
    dd = DataDict({"a": {"b": 1, "c": 2}})
    dd.merge({"a": {"b": 10, "d": 4}})
    assert dd.a.b == 10  # Overwritten
    assert dd.a.c == 2  # Preserved
    assert dd.a.d == 4  # Added


def test_merge_adds_new_keys():
    """Test that merge adds new keys."""
    dd = DataDict({"a": 1})
    dd.merge({"b": 2, "c": 3})
    assert dd.a == 1
    assert dd.b == 2
    assert dd.c == 3


def test_merge_empty_dict():
    """Test merging empty dict (no-op)."""
    dd = DataDict({"a": 1})
    dd.merge({})
    assert dd == {"a": 1}


def test_merge_into_empty_dict():
    """Test merging into empty DataDict."""
    dd = DataDict()
    dd.merge({"a": 1, "b": 2})
    assert dd.a == 1
    assert dd.b == 2


def test_merge_deeply_nested():
    """Test merge with deeply nested structures."""
    dd = DataDict({"level1": {"level2": {"existing": "old", "keep": "this"}}})
    dd.merge({"level1": {"level2": {"existing": "new", "added": "value"}}})
    assert dd.level1.level2.existing == "new"
    assert dd.level1.level2.keep == "this"
    assert dd.level1.level2.added == "value"


def test_merge_wraps_dicts():
    """Test that merge wraps dict values into DataDict."""
    dd = DataDict({"a": 1})
    dd.merge({"b": {"c": 2}})
    assert isinstance(dd.b, DataDict)
    assert dd.b.c == 2


def test_merge_non_dict_to_dict():
    """Test merging dict over non-dict value."""
    dd = DataDict({"a": 123})
    dd.merge({"a": {"b": 1}})
    assert isinstance(dd.a, DataDict)
    assert dd.a.b == 1


def test_merge_dict_to_non_dict():
    """Test merging non-dict over dict value."""
    dd = DataDict({"a": {"b": 1}})
    dd.merge({"a": 123})
    assert dd.a == 123


def test_merge_multiple_times():
    """Test successive merges."""
    dd = DataDict({"a": 1})
    dd.merge({"b": 2})
    dd.merge({"c": 3})
    dd.merge({"a": 10})

    assert dd.a == 10
    assert dd.b == 2
    assert dd.c == 3


def test_merge_with_none_values():
    """Test merge with None values."""
    dd = DataDict({"a": {"b": 1}})
    dd.merge({"a": None})
    assert dd.a is None


def test_merge_on_frozen_raises_error():
    """Test that merge on frozen DataDict raises error."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="frozen"):
        dd.merge({"b": 2})


def test_merge_from_datadict():
    """Test merging from another DataDict."""
    dd1 = DataDict({"a": 1, "b": 2})
    dd2 = DataDict({"b": 20, "c": 3})
    dd1.merge(dd2)

    assert dd1.a == 1
    assert dd1.b == 20
    assert dd1.c == 3


def test_merge_complex_structure():
    """Test merge with complex nested structure."""
    dd = DataDict(
        {
            "database": {
                "primary": {"host": "localhost", "port": 5432},
                "replicas": [],
            },
            "cache": {
                "enabled": True,
            },
        }
    )
    dd.merge(
        {
            "database": {
                "primary": {"port": 5433},
                "replicas": [{"host": "replica1"}],
                "backup": {"host": "backup"},
            },
            "logging": {
                "level": "INFO",
            },
        }
    )

    assert dd.database.primary.host == "localhost"
    assert dd.database.primary.port == 5433
    assert dd.database.replicas == [{"host": "replica1"}]
    assert dd.database.backup.host == "backup"
    assert dd.cache.enabled is True
    assert dd.logging.level == "INFO"
