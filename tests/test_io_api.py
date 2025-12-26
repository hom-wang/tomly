"""
Comprehensive I/O tests for tomly module.
Tests load, loads, dump, dumps with various input/output types.
"""

import io
from pathlib import Path

import pytest

import tomly
from tomly import DataDict

# ==============================================================
# Test loads() function for parsing TOML strings.
# ==============================================================


def test_loads_basic():
    """Test basic TOML string parsing."""
    toml_str = """
        title = "Test"
        version = 1
    """
    data = tomly.loads(toml_str)
    assert data["title"] == "Test"
    assert data["version"] == 1


def test_loads_nested_tables():
    """Test parsing nested TOML tables."""
    toml_str = """
        [server]
        host = "127.0.0.1"
        port = 8080

        [server.ssl]
        enabled = true
    """
    data = tomly.loads(toml_str)
    assert data["server"]["host"] == "127.0.0.1"
    assert data["server"]["port"] == 8080
    assert data["server"]["ssl"]["enabled"] is True


def test_loads_arrays():
    """Test parsing TOML arrays."""
    toml_str = """
        numbers = [1, 2, 3]
        strings = ["a", "b", "c"]
    """
    data = tomly.loads(toml_str)
    assert data["numbers"] == [1, 2, 3]
    assert data["strings"] == ["a", "b", "c"]


def test_loads_array_of_tables():
    """Test parsing array of tables."""
    toml_str = """
        [[items]]
        name = "first"
        value = 1

        [[items]]
        name = "second"
        value = 2
    """
    data = tomly.loads(toml_str)
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "first"
    assert data["items"][1]["value"] == 2


def test_loads_inline_tables():
    """Test parsing inline tables."""
    toml_str = """
        point = { x = 1, y = 2 }
    """
    data = tomly.loads(toml_str)
    assert data["point"]["x"] == 1
    assert data["point"]["y"] == 2


def test_loads_with_none_value():
    """Test loads with none_value parameter."""
    toml_str = """
        key = "null"
    """
    data = tomly.loads(toml_str, none_value="null")
    assert data["key"] is None


def test_loads_multiline_strings():
    """Test parsing multiline strings."""
    toml_str = '''
        text = """
        Line 1
        Line 2
        Line 3"""
    '''
    data = tomly.loads(toml_str)
    assert "Line 1" in data["text"]
    assert "Line 2" in data["text"]


def test_loads_empty_string():
    """Test parsing empty TOML string."""
    toml_str = ""
    data = tomly.loads(toml_str)
    assert data == {}


def test_loads_comments_ignored():
    """Test that comments are properly ignored."""
    toml_str = """
        # This is a comment
        key = "value"  # inline comment
    """
    data = tomly.loads(toml_str)
    assert data["key"] == "value"


# ==============================================================
# Test load() function for various input types.
# ==============================================================


def test_load_from_string():
    """Test loading from raw TOML string."""
    toml_str = """
        key = "value"
    """
    data = tomly.load(toml_str)
    assert data["key"] == "value"


def test_load_from_path(tmp_path):
    """Test loading from Path object."""
    toml_str = """
        key = "value"
    """
    file_path = tmp_path / "test.toml"
    file_path.write_text(toml_str, encoding="utf-8")
    data = tomly.load(file_path)
    assert data["key"] == "value"


def test_load_from_text_stream():
    """Test loading from text stream (StringIO)."""
    toml_str = """
        key = "value"
    """
    stream = io.StringIO(toml_str)
    data = tomly.load(stream)
    assert data["key"] == "value"


def test_load_from_binary_stream():
    """Test loading from binary stream (BytesIO)."""
    toml_str = b"""
        key = "value"
    """
    stream = io.BytesIO(toml_str)
    data = tomly.load(stream)
    assert data["key"] == "value"


def test_load_with_custom_encoding(tmp_path):
    """Test loading with custom encoding."""
    toml_str = """
        text = "中文"
    """
    file_path = tmp_path / "test.toml"
    file_path.write_text(toml_str, encoding="utf-8")
    data = tomly.load(file_path, encoding="utf-8")
    assert data["text"] == "中文"


def test_load_with_none_value():
    """Test load with none_value parameter."""
    toml_str = """
        key = "null"
    """
    stream = io.StringIO(toml_str)
    data = tomly.load(stream, none_value="null")
    assert data["key"] is None


def test_load_empty_file(tmp_path):
    """Test loading empty file."""
    toml_str = ""
    file_path = tmp_path / "empty.toml"
    file_path.write_text(toml_str)
    data = tomly.load(file_path)
    assert data == {}


def test_load_complex_file(tmp_path):
    """Test loading complex TOML file."""
    file_path = tmp_path / "complex.toml"
    content = r'''
        # Basic Types
        title = "TOML Test"
        integer = 42
        float = 3.14
        boolean = true
        date = 1979-05-27T07:32:00Z
        # Strings
        basic_string = "Hello World"
        literal_string = 'C:\Users\path'
        multiline = """
        Line 1
        Line 2"""
        # Arrays
        array = [1, 2, 3]
        nested_array = [[1, 2], [3, 4]]
        string_array = ["a", "b", "c"]
        # Top-level Inline Tables
        inline = { x = 1, y = 2 }
        point = { lat = 25.0, lon = 121.5 }
        # Tables
        [section]
        key = "value"
        number = 100
        # Nested Tables
        [section.nested]
        nested_key = "nested_value"
        nested_number = 999
        inline_in_section = { a = "alpha", b = "beta" }
        # Array of Tables
        [[items]]
        name = "item1"
        value = 10
        [[items]]
        name = "item2"
        value = 20
        # Edge Cases
        [edge_cases]
        empty_string = ""
        negative = -99
        hex = 0xFF
        infinity = inf
        infinity_n = -inf
        none = 'null'
        unicode = "中文 🚀"
        "key with spaces" = "value"
        # Config Section
        [config]
        host = "localhost"
        port = 8080
        debug = true
        tags = ["web", "api"]
    '''

    def _verify_sample_toml(context: dict, conv_none_value: bool = False):
        # console.print(context)

        # Basic Types
        assert context["title"] == "TOML Test"
        assert context["integer"] == 42
        assert context["float"] == 3.14
        assert context["boolean"] is True
        assert "date" in context
        # Strings
        assert context["basic_string"] == "Hello World"
        assert context["literal_string"] == "C:\\Users\\path"
        assert "Line 1" in context["multiline"]
        assert "Line 2" in context["multiline"]
        # Arrays
        assert context["array"] == [1, 2, 3]
        assert context["nested_array"] == [[1, 2], [3, 4]]
        assert context["string_array"] == ["a", "b", "c"]
        # Top-level Inline Tables
        assert context["inline"]["x"] == 1
        assert context["inline"]["y"] == 2
        assert context["point"]["lat"] == 25.0
        assert context["point"]["lon"] == 121.5
        # Tables
        assert context["section"]["key"] == "value"
        assert context["section"]["number"] == 100
        # Nested Tables
        assert context["section"]["nested"]["nested_key"] == "nested_value"
        assert context["section"]["nested"]["nested_number"] == 999
        assert context["section"]["nested"]["inline_in_section"]["a"] == "alpha"
        assert context["section"]["nested"]["inline_in_section"]["b"] == "beta"
        # Array of Tables
        assert len(context["items"]) == 2
        assert context["items"][0]["name"] == "item1"
        assert context["items"][0]["value"] == 10
        assert context["items"][1]["name"] == "item2"
        assert context["items"][1]["value"] == 20
        # Edge Cases
        assert context["edge_cases"]["empty_string"] == ""
        assert context["edge_cases"]["negative"] == -99
        assert context["edge_cases"]["hex"] == 255
        assert context["edge_cases"]["infinity"] == float("inf")
        assert context["edge_cases"]["infinity_n"] == float("-inf")
        if conv_none_value:
            assert context["edge_cases"]["none"] is None
        else:
            assert context["edge_cases"]["none"] == "null"
        assert context["edge_cases"]["unicode"] == "中文 🚀"
        assert context["edge_cases"]["key with spaces"] == "value"
        # Config Section
        assert context["config"]["host"] == "localhost"
        assert context["config"]["port"] == 8080
        assert context["config"]["debug"] is True
        assert context["config"]["tags"] == ["web", "api"]

    file_path.write_text(content)

    data = tomly.load(file_path)
    _verify_sample_toml(data, conv_none_value=False)

    data = tomly.load(file_path, none_value="null")
    _verify_sample_toml(data, conv_none_value=True)


# ==============================================================
# Test dumps() function for serialization to string.
# ==============================================================


def test_dumps_basic():
    """Test basic dictionary serialization."""
    data = {
        "title": "Test",
        "version": 1,
    }
    toml_str = tomly.dumps(data)
    assert 'title = "Test"' in toml_str
    assert "version = 1" in toml_str


def test_dumps_nested():
    """Test nested dictionary serialization."""
    data = {
        "server": {
            "host": "localhost",
            "port": 8080,
        },
    }
    toml_str = tomly.dumps(data)
    assert "[server]" in toml_str
    assert 'host = "localhost"' in toml_str


def test_dumps_arrays():
    """Test array serialization."""
    data = {
        "numbers": [1, 2, 3],
        "strings": ["a", "b"],
    }
    toml_str = tomly.dumps(data)
    assert "[1, 2, 3]" in toml_str or "1, 2, 3" in toml_str


def test_dumps_with_none_value():
    """Test dumps with none_value parameter."""
    data = {"key": None}
    toml_str = tomly.dumps(data, none_value="null")
    assert 'key = "null"' in toml_str


def test_dumps_pretty():
    """Test pretty printing mode."""
    data = {"a": 1, "b": {"c": 2}}
    toml_str = tomly.dumps(data, pretty=True)
    # Pretty mode should add extra formatting
    assert "a = 1" in toml_str
    assert "[b]" in toml_str


def test_dumps_datadict():
    """Test serializing DataDict instance."""
    dd = DataDict(
        {
            "a": {"b": 1},
        }
    )
    toml_str = tomly.dumps(dd)
    assert "a" in toml_str
    assert "b" in toml_str


def test_dumps_roundtrip():
    """Test that dumps -> loads is lossless."""
    original = {
        "title": "Test",
        "config": {
            "host": "localhost",
            "port": 8080,
        },
        "tags": ["web", "api"],
    }
    toml_str = tomly.dumps(original)
    restored = tomly.loads(toml_str)
    assert restored == original


def test_dumps_empty_dict():
    """Test serializing empty dictionary."""
    data = {}
    toml_str = tomly.dumps(data)
    assert toml_str.strip() == ""


def test_dumps_special_characters():
    """Test serializing strings with special characters."""
    data = {
        "text": "Line 1\nLine 2",
        "path": "C:\\Users\\test",
    }
    toml_str = tomly.dumps(data)
    restored = tomly.loads(toml_str)
    assert restored["text"] == data["text"]


# ==============================================================
# Test dump() function for various output types.
# ==============================================================


def test_dump_to_path(tmp_path):
    """Test dumping to Path object."""
    file_path = tmp_path / "output.toml"
    data = {"key": "value"}
    num_written = tomly.dump(data, file_path)

    assert num_written > 0
    content = file_path.read_text()
    assert 'key = "value"' in content


def test_dump_to_text_stream():
    """Test dumping to text stream."""
    stream = io.StringIO()
    data = {"key": "value"}
    num_written = tomly.dump(data, stream)

    assert num_written > 0
    content = stream.getvalue()
    assert 'key = "value"' in content


def test_dump_to_binary_stream():
    """Test dumping to binary stream."""
    stream = io.BytesIO()
    data = {"key": "value"}
    num_written = tomly.dump(data, stream)

    assert num_written > 0
    content = stream.getvalue().decode("utf-8")
    assert 'key = "value"' in content


def test_dump_with_pretty(tmp_path):
    """Test dump with pretty mode."""
    file_path = tmp_path / "pretty.toml"
    data = {"a": 1, "b": {"c": 2}}
    tomly.dump(data, file_path, pretty=True)

    content = file_path.read_text()
    assert "a = 1" in content


def test_dump_with_none_value(tmp_path):
    """Test dump with none_value parameter."""
    file_path = tmp_path / "none.toml"
    data = {"key": None}
    tomly.dump(data, file_path, none_value="N/A")

    content = file_path.read_text()
    assert 'key = "N/A"' in content


def test_dump_with_custom_encoding(tmp_path):
    """Test dump with custom encoding."""
    file_path = tmp_path / "encoded.toml"
    data = {"text": "中文"}
    tomly.dump(data, file_path, encoding="utf-8")

    content = file_path.read_text(encoding="utf-8")
    assert "中文" in content


def test_dump_returns_byte_count(tmp_path):
    """Test that dump returns correct byte/character count."""
    file_path = tmp_path / "test.toml"
    data = {"key": "value"}
    num_written = tomly.dump(data, file_path)

    actual_size = file_path.stat().st_size
    assert num_written == actual_size


def test_dump_invalid_file_type_raises():
    """Test that invalid file type raises TypeError."""
    data = {"key": "value"}
    with pytest.raises(TypeError, match="invalid file type"):
        tomly.dump(data, object())


def test_dump_complex_structure(tmp_path):
    """Test dumping complex nested structure."""
    file_path = tmp_path / "complex.toml"
    data = {
        "project": {
            "name": "tomly",
            "version": "0.1.0",
        },
        "dependencies": ["rtoml", "pytest"],
        "servers": [
            {
                "name": "prod",
                "host": "prod.example.com",
            },
            {
                "name": "dev",
                "host": "dev.example.com",
            },
        ],
    }
    tomly.dump(data, file_path)

    # Verify by loading back
    restored = tomly.load(file_path)
    assert restored["project"]["name"] == "tomly"
    assert len(restored["servers"]) == 2


# ==============================================================
# Test full roundtrip: load -> modify -> dump -> load.
# ==============================================================


def test_file_roundtrip(tmp_path):
    """Test complete file I/O cycle."""
    file_path = tmp_path / "config.toml"

    # Initial data
    original = {
        "database": {
            "host": "localhost",
            "port": 5432,
        }
    }

    # Write
    tomly.dump(original, file_path)

    # Read and modify
    config = DataDict(tomly.load(file_path))
    config.database.port = 5433
    config.database.ssl = True

    # Write modified
    tomly.dump(config, file_path)

    # Read and verify
    final = tomly.load(file_path)
    assert final["database"]["port"] == 5433
    assert final["database"]["ssl"] is True
    assert final["database"]["host"] == "localhost"


def test_string_roundtrip():
    """Test dumps -> loads roundtrip."""
    original = {
        "app": {"name": "test", "version": "1.0"},
        "features": ["auth", "api", "logging"],
    }

    toml_str = tomly.dumps(original)
    restored = tomly.loads(toml_str)

    assert restored == original


def test_none_value_roundtrip():
    """Test roundtrip with None values."""
    original = {
        "key1": None,
        "key2": "value",
    }

    toml_str = tomly.dumps(original, none_value="null")
    restored = tomly.loads(toml_str, none_value="null")

    assert restored["key1"] is None
    assert restored["key2"] == "value"


def test_datadict_roundtrip():
    """Test roundtrip with DataDict."""
    original = DataDict({"nested": {"deep": {"value": 123}}})

    toml_str = tomly.dumps(original)
    restored = DataDict(tomly.loads(toml_str))

    assert restored.nested.deep.value == 123


# ==============================================================
# Test error handling in I/O operations.
# ==============================================================


def test_loads_invalid_toml():
    """Test that invalid TOML raises error."""
    invalid_toml = "this is [ not valid toml"
    with pytest.raises(expected_exception=tomly.rtoml.TomlParsingError):  # rtoml will raise an error
        tomly.loads(invalid_toml)


def test_load_nonexistent_file():
    """Test loading non-existent file raises error."""
    with pytest.raises(expected_exception=FileNotFoundError):
        tomly.load(Path("/nonexistent/file.toml"))


def test_dump_to_readonly_path(tmp_path):
    """Test dumping to read-only location."""
    file_path = tmp_path / "readonly.toml"
    file_path.write_text("test")
    file_path.chmod(0o444)  # Read-only

    try:
        with pytest.raises(PermissionError):
            tomly.dump({"key": "value"}, file_path)
    finally:
        file_path.chmod(0o644)  # Restore for cleanup


# ==============================================================
# Test edge cases in I/O operations.
# ==============================================================


def test_very_large_structure():
    """Test handling very large data structures."""
    large_data = {f"key_{i}": {"nested": {"value": i}} for i in range(1000)}
    toml_str = tomly.dumps(large_data)
    restored = tomly.loads(toml_str)
    assert len(restored) == 1000
    assert restored["key_500"]["nested"]["value"] == 500


def test_deeply_nested_structure():
    """Test handling deeply nested structures."""
    data = {}
    current = data
    for i in range(20):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    toml_str = tomly.dumps(data)
    restored = tomly.loads(toml_str)

    # Navigate to deep value
    current = restored
    for i in range(20):
        current = current[f"level{i}"]
    assert current["value"] == "deep"


def test_unicode_handling():
    """Test Unicode character handling."""
    data = {
        "chinese": "中文",
        "emoji": "🚀🎉",
        "russian": "Привет",
        "arabic": "مرحبا",
    }
    toml_str = tomly.dumps(data)
    restored = tomly.loads(toml_str)
    assert restored == data


def test_special_float_values():
    """Test special float values."""
    data = {
        "inf": float("inf"),
        "neg_inf": float("-inf"),
    }
    toml_str = tomly.dumps(data)
    restored = tomly.loads(toml_str)
    assert restored["inf"] == float("inf")
    assert restored["neg_inf"] == float("-inf")


# ==============================================================
# Test sanitize API.
# ==============================================================


def test_sanitize_path():
    """Test sanitize specifically with Path."""
    p = Path("/tmp/test")
    assert tomly.sanitize(p) == str(p)


def test_sanitize_iterable():
    """Test sanitize with tuple/set to cover list|tuple|set branch fully."""
    s = {Path("a"), Path("b")}
    res = tomly.sanitize(s)
    assert isinstance(res, list)
    assert str(Path("a")) in res


def test_sanitize_nested():
    """Ensure recursive sanitize works."""
    data = {"a": [Path("p")]}
    res = tomly.sanitize(data)
    assert res["a"][0] == "p"


def test_sanitize_leaf():
    """Test sanitize on a simple leaf value."""
    assert tomly.sanitize(42) == 42
    assert tomly.sanitize("s") == "s"


def test_dumps_with_sanitize_true():
    """Test dumps with sanitize=True explicitly."""
    data = {"path": Path("/test")}
    toml_str = tomly.dumps(data, sanitize=True)
    assert 'path = "/test"' in toml_str
