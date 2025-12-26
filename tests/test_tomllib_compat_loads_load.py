"""
Compatibility contract tests: tomllib vs tomly for load() and loads().
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest

import tomly

tomllib = pytest.importorskip("tomllib")  # Python >= 3.11


# ==============================================================
# Helpers
# ==============================================================


def assert_same_structure(a: Any, b: Any, path: str = "$") -> None:
    """
    Deep-compare values AND types recursively.
    tomllib returns native datetime/date/time objects for TOML temporal types,
    so a "fully compatible" parser must match those types too.
    """
    assert type(a) is type(b), f"type mismatch at {path}: {type(a)} != {type(b)}"

    if isinstance(a, dict):
        assert a.keys() == b.keys(), f"dict keys mismatch at {path}: {a.keys()} != {b.keys()}"
        for k in a:
            assert_same_structure(a[k], b[k], f"{path}.{k!r}")
        return

    if isinstance(a, list):
        assert len(a) == len(b), f"list length mismatch at {path}: {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            assert_same_structure(x, y, f"{path}[{i}]")
        return

    # primitives / datetime-like objects
    assert a == b, f"value mismatch at {path}: {a!r} != {b!r}"


def parse_with_tomllib_loads(toml_text: str) -> Any:
    return tomllib.loads(toml_text)


def parse_with_tomly_loads(toml_text: str) -> Any:
    return tomly.loads(toml_text)


def parse_with_tomllib_load_binary(toml_text: str) -> Any:
    return tomllib.load(io.BytesIO(toml_text.encode("utf-8")))


def parse_with_tomly_load_binary(toml_text: str) -> Any:
    return tomly.load(io.BytesIO(toml_text.encode("utf-8")))


# ==============================================================
# Test cases (cover TOML surface supported by tomllib)
# ==============================================================

TOML_CASES: list[tuple[str, str]] = [
    (
        "basic_scalars",
        """
        title = "Test"
        enabled = true
        count = 42
        pi = 3.14
        """,
    ),
    (
        "strings_escapes_unicode",
        r"""
        a = "line1\nline2\tend"
        b = "unicode: \u03B1 \u03B2 \u03B3"
        c = 'literal \n not escaped'
        """,
    ),
    (
        "multiline_strings",
        """
        a = \"\"\"Line 1
        Line 2
        Line 3\"\"\"
        b = '''literal
        line
        block'''
        """,
    ),
    (
        "integers_formats",
        """
        dec = 1_000_000
        hex = 0xDEADBEEF
        oct = 0o755
        bin = 0b1101_0101
        """,
    ),
    (
        "floats_formats",
        """
        a = 1.0
        b = 1e3
        c = -0.01
        d = +3.1415
        """,
    ),
    (
        "arrays_mixed_and_nested",
        """
        a = [1, 2, 3]
        b = ["a", "b", "c"]
        c = [[1, 2], [3, 4]]
        """,
    ),
    (
        "inline_tables",
        """
        point = { x = 1, y = 2 }
        nested = { a = { b = 1 } }
        """,
    ),
    (
        "tables_and_nested_tables",
        """
        [server]
        host = "127.0.0.1"
        port = 8080

        [server.ssl]
        enabled = true
        """,
    ),
    (
        "array_of_tables",
        """
        [[items]]
        name = "first"
        value = 1

        [[items]]
        name = "second"
        value = 2
        """,
    ),
    (
        "dotted_keys_and_quoted_keys",
        """
        a.b.c = 1
        "a.b".c = 2
        "weird key" = 3
        """,
    ),
    (
        "dates_times",
        """
        date1 = 1979-05-27
        time1 = 07:32:00
        dt1 = 1979-05-27T07:32:00
        dt2 = 1979-05-27T07:32:00Z
        dt3 = 1979-05-27T07:32:00+07:00
        """,
    ),
    (
        "comments_and_whitespace",
        """
        # top comment
        key = "value" # inline comment

        [t]   # table comment
        a = 1
        """,
    ),
]


# ==============================================================
# Core compatibility: loads(str)
# ==============================================================


@pytest.mark.parametrize("name,toml_text", TOML_CASES)
def test_loads_str_fully_compatible(name: str, toml_text: str):
    """tomly.loads(str) must match tomllib.loads(str) exactly (values + types)."""
    a = parse_with_tomllib_loads(toml_text)
    b = parse_with_tomly_loads(toml_text)
    assert_same_structure(a, b)


def test_loads_empty_string():
    """Empty TOML should parse to {} consistently."""
    a = tomllib.loads("")
    b = tomly.loads("")
    assert_same_structure(a, b)
    assert a == {}


# ==============================================================
# Core compatibility: load(binary_io)
# ==============================================================


@pytest.mark.parametrize("name,toml_text", TOML_CASES)
def test_load_binary_fully_compatible(name: str, toml_text: str):
    """tomly.load(binary_io) must match tomllib.load(binary_io) exactly."""
    a = parse_with_tomllib_load_binary(toml_text)
    b = parse_with_tomly_load_binary(toml_text)
    assert_same_structure(a, b)


# ==============================================================
# Cross-check: tomllib loads == tomllib load(binary)
# (sanity check, catches test-data mistakes)
# ==============================================================


@pytest.mark.parametrize("name,toml_text", TOML_CASES)
def test_tomllib_loads_equals_load_binary(name: str, toml_text: str):
    """tomllib should be self-consistent; if not, the test case is suspicious."""
    a = parse_with_tomllib_loads(toml_text)
    b = parse_with_tomllib_load_binary(toml_text)
    assert_same_structure(a, b)


# ==============================================================
# tomly extended input forms must preserve semantics
# ==============================================================


@pytest.mark.parametrize("name,toml_text", TOML_CASES)
def test_tomly_load_extended_inputs_match_tomllib(name: str, toml_text: str, tmp_path: Path):
    """
    tomly supports extra load() input types.
    For the same content, all tomly input forms must match tomllib parsing.
    """
    # baseline: tomllib.loads
    expected = tomllib.loads(toml_text)

    # tomly: raw string (tomly.load accepts str content)
    got_str = tomly.load(toml_text)
    assert_same_structure(expected, got_str)

    # tomly: path
    p = tmp_path / f"{name}.toml"
    p.write_text(toml_text, encoding="utf-8")
    got_path = tomly.load(p)
    assert_same_structure(expected, got_path)

    # tomly: text stream
    got_textio = tomly.load(io.StringIO(toml_text))
    assert_same_structure(expected, got_textio)

    # tomly: binary stream
    got_binio = tomly.load(io.BytesIO(toml_text.encode("utf-8")))
    assert_same_structure(expected, got_binio)


# ==============================================================
# Negative tests: invalid TOML must fail (both should raise)
# We do NOT require identical exception classes/messages.
# ==============================================================

INVALID_TOML_CASES: list[tuple[str, str]] = [
    ("unterminated_string", 'a = "oops\n'),
    ("bad_int", "a = 00\n"),
    ("bad_table_header", "[[x]\na=1\n"),
    ("duplicate_keys", "a=1\na=2\n"),
]


@pytest.mark.parametrize("name,toml_text", INVALID_TOML_CASES)
def test_invalid_toml_must_raise_in_both(name: str, toml_text: str):
    """For invalid TOML, both tomllib and tomly must raise an exception."""
    with pytest.raises(Exception):
        tomllib.loads(toml_text)

    with pytest.raises(Exception):
        tomly.loads(toml_text)

    with pytest.raises(Exception):
        tomllib.load(io.BytesIO(toml_text.encode("utf-8")))

    with pytest.raises(Exception):
        tomly.load(io.BytesIO(toml_text.encode("utf-8")))
