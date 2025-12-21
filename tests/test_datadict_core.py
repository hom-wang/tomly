"""
Core functionality tests for DataDict class.
Tests basic initialization, access patterns, and wrapping behavior.
"""

import pytest

from tomly import DataDict

# ==============================================================
# Test DataDict initialization and construction.
# ==============================================================


def test_empty_initialization():
    """
    Test creating an empty DataDict.
    """
    dd = DataDict()
    assert len(dd) == 0
    assert isinstance(dd, dict)


def test_dict_initialization():
    """
    Test initialization from a standard dict.
    """
    data = {
        "a": 1,
        "b": {
            "c": 2,
        },
    }
    dd = DataDict(data)
    assert dd["a"] == 1
    assert dd["b"]["c"] == 2
    assert isinstance(dd["b"], DataDict)


def test_kwargs_initialization():
    """
    Test initialization using keyword arguments.
    """
    dd = DataDict(x=1, y=2)
    assert dd.x == 1
    assert dd.y == 2


def test_mixed_initialization():
    """
    Test initialization with both dict and kwargs.
    """
    dd = DataDict({"a": 1}, b=2)
    assert dd.a == 1
    assert dd.b == 2


def test_nested_dict_wrapping():
    """
    Test that nested dicts are automatically wrapped.
    """
    data = {
        "level1": {
            "level2": {
                "level3": {
                    "value": "deep",
                }
            }
        }
    }
    dd = DataDict(data)
    assert isinstance(dd.level1, DataDict)
    assert isinstance(dd.level1.level2, DataDict)
    assert isinstance(dd.level1.level2.level3, DataDict)
    assert dd.level1.level2.level3.value == "deep"


def test_list_with_dicts_wrapping():
    """
    Test that dicts inside lists are wrapped.
    """
    data = {
        "items_": [
            {
                "id": 1,
                "name": "first",
            },
            {
                "id": 2,
                "name": "second",
            },
        ]
    }
    dd = DataDict(data)
    assert isinstance(dd.items_[0], DataDict)
    assert isinstance(dd.items_[1], DataDict)
    assert dd.items_[0].id == 1
    assert dd.items_[1].name == "second"


def test_list_without_dicts_not_wrapped():
    """
    Test that lists without dicts remain unchanged.
    """
    data = {
        "numbers": [1, 2, 3],
        "strings": ["a", "b", "c"],
    }
    dd = DataDict(data)
    assert dd.numbers == [1, 2, 3]
    assert dd.strings == ["a", "b", "c"]


def test_empty_list_handling():
    """
    Test that empty lists are handled correctly.
    """
    data = {
        "empty": [],
    }

    dd = DataDict(data)
    assert dd.empty == []


def test_already_datadict_not_rewrapped():
    """
    Test that existing DataDict instances are not rewrapped.
    """
    inner = DataDict({"x": 1})
    outer = DataDict({"inner": inner})
    assert outer.inner is inner


# ==============================================================
# Test attribute-style access patterns.
# ==============================================================


def test_basic_attribute_get():
    """
    Test reading attributes via dot notation.
    """
    dd = DataDict(
        {
            "name": "test",
            "count": 42,
        }
    )
    assert dd.name == "test"
    assert dd.count == 42


def test_basic_attribute_set():
    """
    Test setting attributes via dot notation.
    """
    dd = DataDict()
    dd.name = "test"
    dd.count = 42
    assert dd["name"] == "test"
    assert dd["count"] == 42


def test_attribute_delete():
    """
    Test deleting attributes via del statement.
    """
    dd = DataDict(
        {
            "x": 1,
            "y": 2,
        }
    )
    del dd.x
    assert "x" not in dd
    assert dd.y == 2


def test_nonexistent_attribute_raises_error():
    """
    Test that accessing non-existent attributes raises AttributeError.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    with pytest.raises(AttributeError, match="no attribute 'b'"):
        _ = dd.b


def test_delete_nonexistent_attribute_raises_error():
    """
    Test that deleting non-existent attributes raises AttributeError.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    with pytest.raises(AttributeError, match="no attribute 'b'"):
        del dd.b


def test_invalid_identifier_keys():
    """
    Test that keys with invalid Python identifiers require dict access.
    """
    dd = DataDict(
        {
            "key-with-dash": 1,
            "key with space": 2,
            "123numeric": 3,
        }
    )

    # Should work with dict access
    assert dd["key-with-dash"] == 1
    assert dd["key with space"] == 2
    assert dd["123numeric"] == 3

    # Should fail with attribute access
    with pytest.raises(AttributeError):
        _ = dd.key_with_dash


def test_private_attributes_not_intercepted():
    """
    Test that private attributes (starting with _) work normally.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    dd._private = "test"
    assert hasattr(dd, "_private")
    assert dd._private == "test"
    assert "_private" not in dd  # Should not be in dict keys


def test_nested_attribute_modification():
    """
    Test modifying nested attributes.
    """
    dd = DataDict(
        {
            "server": {
                "host": "localhost",
                "port": 8080,
            }
        }
    )
    dd.server.port = 9000
    assert dd["server"]["port"] == 9000
    assert dd.server.port == 9000


def test_dir_includes_valid_keys():
    """
    Test that __dir__ includes valid identifier keys.
    """
    dd = DataDict(
        {
            "valid_key": 1,
            "invalid-key": 2,
            "123": 3,
        }
    )
    dir_result = dir(dd)
    assert "valid_key" in dir_result
    assert "invalid-key" not in dir_result
    assert "123" not in dir_result


# ==============================================================
# Test that DataDict maintains dict interface compatibility.
# ==============================================================


def test_len():
    """
    Test len() function.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )
    assert len(dd) == 3


def test_contains():
    """
    Test 'in' operator.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    assert "a" in dd
    assert "c" not in dd


def test_keys():
    """
    Test keys() method.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    keys = list(dd.keys())
    assert set(keys) == {"a", "b"}


def test_values():
    """
    Test values() method.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    values = list(dd.values())
    assert set(values) == {1, 2}


def test_items():
    """
    Test items() method.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    items = list(dd.items())
    assert set(items) == {("a", 1), ("b", 2)}


def test_get_with_default():
    """
    Test get() method with default value.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    assert dd.get("a") == 1
    assert dd.get("b") is None
    assert dd.get("b", "default") == "default"


def test_iteration():
    """
    Test iterating over keys.
    """
    dd = DataDict(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )
    keys = [k for k in dd]  # noqa: C416
    assert set(keys) == {"a", "b", "c"}

    keys = list(dd)
    assert set(keys) == {"a", "b", "c"}


def test_equality():
    """
    Test equality comparison.
    """
    dd1 = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    dd2 = DataDict(
        {
            "a": 1,
            "b": 2,
        }
    )
    dd3 = DataDict(
        {
            "a": 1,
            "b": 3,
        }
    )

    assert dd1 == dd2
    assert dd1 != dd3
    assert dd1 == {"a": 1, "b": 2}  # Should equal regular dict


def test_repr():
    """
    Test string representation.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    repr_str = repr(dd)
    assert "a" in repr_str
    assert "1" in repr_str


# ==============================================================
# Test the automatic wrapping and unwrapping of values.
# ==============================================================


def test_new_dict_value_gets_wrapped():
    """
    Test that newly assigned dict values are wrapped.
    """
    dd = DataDict()
    dd.config = {
        "host": "localhost",
    }
    assert isinstance(dd.config, DataDict)
    assert dd.config.host == "localhost"


def test_nested_assignment_wrapping():
    """
    Test wrapping on nested assignment.
    """
    dd = DataDict(
        {
            "level1": {},
        }
    )
    dd.level1.level2 = {
        "value": 42,
    }
    assert isinstance(dd.level1.level2, DataDict)
    assert dd.level1.level2.value == 42


def test_scalar_values_not_wrapped():
    """
    Test that scalar values remain unchanged.
    """
    dd = DataDict(
        {
            "int": 42,
            "float": 3.14,
            "str": "hello",
            "bool": True,
            "none": None,
        }
    )
    assert dd.int == 42
    assert dd.float == 3.14
    assert dd.str == "hello"
    assert dd.bool is True
    assert dd.none is None


def test_mixed_list_wrapping():
    """
    Test wrapping of lists with mixed content.
    """
    dd = DataDict(
        {
            "mixed": [
                1,
                "string",
                {"nested": "dict"},
                [1, 2, 3],
                None,
            ],
        }
    )
    assert dd.mixed[0] == 1
    assert dd.mixed[1] == "string"
    assert isinstance(dd.mixed[2], DataDict)
    assert dd.mixed[2].nested == "dict"
    assert dd.mixed[3] == [1, 2, 3]
    assert dd.mixed[4] is None


def test_update_wraps_values():
    """
    Test that update() wraps new values.
    """
    dd = DataDict(
        {
            "a": 1,
        }
    )
    dd.update(
        {
            "b": {
                "c": 2,
            }
        }
    )
    assert isinstance(dd.b, DataDict)
    assert dd.b.c == 2

    dd = DataDict(
        {
            "a": 1,
        },
        coerce_mapping=False,
    )
    dd.update(
        {
            "b": {
                "c": 2,
            }
        }
    )
    assert isinstance(dd.b, dict)
    assert dd.b["c"] == 2


def test_setdefault_wraps_values():
    """
    Test that setdefault() wraps values.
    """
    dd = DataDict()
    result = dd.setdefault("config", {"port": 8080})
    assert isinstance(result, DataDict)
    assert isinstance(dd.config, DataDict)
    assert dd.config.port == 8080

    dd = DataDict(coerce_mapping=False)
    result = dd.setdefault("config", {"port": 8080})
    assert isinstance(result, dict)
    assert isinstance(dd.config, dict)
    assert dd.config["port"] == 8080
