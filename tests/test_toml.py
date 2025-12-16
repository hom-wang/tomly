import math
from pathlib import Path

import rtoml
import tomllib
from rich.console import Console

import tomly

console = Console()


def verify_sample_toml(context: dict, none_value: str = None) -> bool:
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
    assert math.isinf(context["edge_cases"]["infinity"])
    if none_value is None:
        assert context["edge_cases"]["none"] == "null"
    else:
        assert context["edge_cases"]["none"] is None
    assert context["edge_cases"]["unicode"] == "中文 🚀"
    assert context["edge_cases"]["key with spaces"] == "value"
    # Config Section
    assert context["config"]["host"] == "localhost"
    assert context["config"]["port"] == 8080
    assert context["config"]["debug"] is True
    assert context["config"]["tags"] == ["web", "api"]

    return True


# Test 1: loads() --------

with open("sample.toml", "r") as f:
    toml_string = f.read()

console.print("--- tomllib.loads() ---")
ret = tomllib.loads(toml_string)
verify_sample_toml(ret)

console.print("--- rtoml.loads() ---")
ret = rtoml.loads(toml_string, none_value="null")
verify_sample_toml(ret, none_value="null")

console.print("--- tomly.loads() ---")
ret = tomly.loads(toml_string, none_value="null")
verify_sample_toml(ret, none_value="null")

# Test 2: load() --------

with open("sample.toml", "rb") as f:
    console.print("--- tomllib.load() ---")
    toml_dict = tomllib.load(f)

# with open("sample.toml", "rb") as f:
with open("sample.toml", "r") as f:
    console.print("--- rtoml.load() ---")
    toml_dict = rtoml.load(f)

with open("sample.toml", "rb") as f:
    console.print("--- tomly.load() ---")
    toml_dict = tomly.load(f)
