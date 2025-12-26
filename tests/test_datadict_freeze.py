"""
Immutability and freeze mechanism tests for DataDict.
Tests the freeze() method and all mutation prevention.
"""

import pytest

from tomly import DataDict

# ==============================================================
# Test the freeze functionality for immutability.
# ==============================================================


def test_freeze_returns_self():
    """Test that freeze() returns the instance for chaining."""
    dd = DataDict({"a": 1})
    result = dd.freeze()
    assert result is dd


def test_freeze_sets_frozen_flag():
    """Test that freeze() sets the internal _frozen flag."""
    dd = DataDict({"a": 1})
    assert dd._frozen is False
    dd.freeze()
    assert dd._frozen is True


def test_frozen_prevents_setitem():
    """Test that frozen DataDict prevents __setitem__."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd["b"] = 2


def test_frozen_prevents_attribute_assignment():
    """Test that frozen DataDict prevents attribute assignment."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.b = 2


def test_frozen_prevents_delitem():
    """Test that frozen DataDict prevents __delitem__."""
    dd = DataDict({"a": 1, "b": 2}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        del dd["a"]


def test_frozen_prevents_attribute_deletion():
    """Test that frozen DataDict prevents del attribute."""
    dd = DataDict({"a": 1, "b": 2}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        del dd.a


def test_frozen_prevents_clear():
    """Test that frozen DataDict prevents clear()."""
    dd = DataDict({"a": 1, "b": 2}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.clear()


def test_frozen_prevents_pop():
    """Test that frozen DataDict prevents pop()."""
    dd = DataDict({"a": 1, "b": 2}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.pop("a")


def test_frozen_prevents_popitem():
    """Test that frozen DataDict prevents popitem()."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.popitem()


def test_frozen_prevents_update():
    """Test that frozen DataDict prevents update()."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.update({"b": 2})


def test_frozen_prevents_setdefault():
    """Test that frozen DataDict prevents setdefault()."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.setdefault("b", 2)


def test_frozen_prevents_set_nested():
    """Test that frozen DataDict prevents set_nested()."""
    dd = DataDict({"a": {"b": 1}}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.set_nested("a.c", 2)


def test_frozen_prevents_delete_nested():
    """Test that frozen DataDict prevents delete_nested()."""
    dd = DataDict({"a": {"b": 1}}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.delete_nested("a.b")


def test_frozen_prevents_merge():
    """Test that frozen DataDict prevents merge()."""
    dd = DataDict({"a": 1}).freeze()
    with pytest.raises(TypeError, match="Cannot modify a frozen DataDict"):
        dd.merge({"b": 2})


def test_freeze_is_recursive():
    """Test that freeze() recursively freezes nested DataDicts."""
    dd = DataDict({"level1": {"level2": {"level3": {"value": 1}}}})
    dd.freeze()

    # All levels should be frozen
    assert dd._frozen is True
    assert dd.level1._frozen is True
    assert dd.level1.level2._frozen is True
    assert dd.level1.level2.level3._frozen is True


def test_nested_frozen_prevents_modification():
    """Test that nested frozen DataDicts prevent modification."""
    dd = DataDict({"outer": {"inner": {"value": 1}}}).freeze()

    with pytest.raises(TypeError):
        dd.outer.inner.value = 2

    with pytest.raises(TypeError):
        dd.outer.new_key = "test"


def test_freeze_idempotent():
    """Test that calling freeze() multiple times is safe."""
    dd = DataDict({"a": 1})
    dd.freeze()
    dd.freeze()  # Should not raise error
    assert dd._frozen is True


def test_frozen_allows_read_operations():
    """Test that frozen DataDict allows all read operations."""
    dd = DataDict({"a": 1, "b": {"c": 2}, "d": [3, 4]}).freeze()

    # All read operations should work
    assert dd.a == 1
    assert dd["b"]["c"] == 2
    assert dd.get("a") == 1
    assert dd.get("missing", "default") == "default"
    assert "a" in dd
    assert len(dd) == 3
    assert list(dd.keys()) == ["a", "b", "d"]
    assert dd.get_nested("b.c") == 2


def test_frozen_allows_conversion_operations():
    """Test that frozen DataDict allows conversion operations."""
    dd = DataDict({"a": 1, "b": {"c": 2}}).freeze()

    # Conversions should work
    as_dict = dd.to_dict()
    assert isinstance(as_dict, dict)
    assert not isinstance(as_dict, DataDict)

    flattened = dd.flatten()
    assert isinstance(flattened, dict)
    assert "b.c" in flattened


def test_freeze_with_lists_containing_datadicts():
    """Test freezing DataDicts that contain lists with DataDicts."""
    dd = DataDict(
        {
            "items_": [
                {"id": 1, "name": "first"},
                {"id": 2, "name": "second"},
            ]
        }
    ).freeze()

    # Top level and nested dicts should be frozen
    assert dd._frozen is True
    assert dd.items_[0]._frozen is True
    assert dd.items_[1]._frozen is True

    with pytest.raises(TypeError):
        dd.items_[0].id = 999


def test_partially_frozen_structure():
    """Test behavior with partially frozen structures."""
    inner = DataDict({"x": 1})
    outer = DataDict({"inner": inner})

    # Freeze only inner
    inner.freeze()

    # Inner should be frozen, outer should not
    assert inner._frozen is True
    assert outer._frozen is False

    # Can't modify inner
    with pytest.raises(TypeError):
        inner.x = 2

    # Can modify outer
    outer.y = 2
    assert outer.y == 2


def test_freeze_empty_datadict():
    """Test freezing an empty DataDict."""
    dd = DataDict().freeze()
    assert dd._frozen is True
    assert len(dd) == 0

    with pytest.raises(TypeError):
        dd.a = 1


def test_frozen_error_message_clarity():
    """Test that frozen errors have clear messages."""
    dd = DataDict({"a": 1}).freeze()

    try:
        dd.b = 2
    except TypeError as e:
        assert "frozen" in str(e).lower()
        assert "DataDict" in str(e)


def test_modification_sequence_before_and_after_freeze():
    """Test normal modification then freeze prevents further changes."""
    dd = DataDict({"a": 1})

    # Before freeze: modifications work
    dd.b = 2
    dd.c = {"d": 3}
    assert dd.b == 2
    assert dd.c.d == 3

    # Freeze
    dd.freeze()

    # After freeze: modifications fail
    with pytest.raises(TypeError):
        dd.e = 4

    with pytest.raises(TypeError):
        dd.c.f = 5


def test_frozen_with_complex_nested_structure():
    """Test freezing a complex nested structure."""
    dd = DataDict(
        {
            "database": {
                "primary": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "admin", "password": "secret"},
                },
                "replicas": [
                    {"host": "replica1", "port": 5433},
                    {"host": "replica2", "port": 5434},
                ],
            },
            "cache": {"redis": {"host": "localhost", "port": 6379}},
        }
    ).freeze()

    # Verify all levels are frozen
    assert dd._frozen is True
    assert dd.database._frozen is True
    assert dd.database.primary._frozen is True
    assert dd.database.primary.credentials._frozen is True
    assert dd.database.replicas[0]._frozen is True
    assert dd.database.replicas[1]._frozen is True
    assert dd.cache._frozen is True
    assert dd.cache.redis._frozen is True

    # Verify none can be modified
    with pytest.raises(TypeError):
        dd.database.primary.host = "remote"

    with pytest.raises(TypeError):
        dd.database.replicas[0].port = 9999

    with pytest.raises(TypeError):
        dd.cache.redis.port = 6380
