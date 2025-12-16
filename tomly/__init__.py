from io import BufferedIOBase, TextIOBase
from pathlib import Path
from typing import Any, BinaryIO, TextIO

import rtoml

from ._version import __version__  # noqa: F401

__all__ = [
    "load",
    "loads",
    "dumps",
    "dump",
]


def loads(toml: str, *, none_value: str | None = None) -> dict[str, Any]:
    """
    Parse TOML content from a string.

    Parameters:
        toml (str):
            TOML-formatted string
        none_value (str | None):
            String value to be interpreted as None (e.g. none_value="null" maps TOML "null" to `None`)

    Returns:
        (dict[str, Any]):
            Parsed TOML data as a dictionary
    """
    return rtoml.loads(toml, none_value=none_value)


def load(toml: str | Path | TextIO | BinaryIO, *, none_value: str | None = None, encoding: str = "utf-8") -> dict[str, Any]:
    """
    Load and parse TOML content from various input sources.

    Supported inputs:
        - File path
        - Text stream
        - Binary stream
        - Raw TOML string

    Parameters:
        toml (str | Path | TextIO | BinaryIO):
            TOML source
        none_value (str | None):
            String value to be interpreted as None (e.g. none_value="null" maps TOML "null" to `None`)
        encoding (str):
            Text encoding used for file or binary input

    Returns:
        (dict[str, Any]):
            Parsed TOML data as a dictionary
    """
    if isinstance(toml, Path):
        toml = toml.read_text(encoding=encoding)

    # TextIO
    elif isinstance(toml, TextIOBase):
        toml = toml.read()

    # BinaryIO
    elif isinstance(toml, BufferedIOBase):
        toml = toml.read().decode(encoding)

    return loads(toml, none_value=none_value)


def dumps(obj: Any, *, pretty: bool = False, none_value: str | None = "null") -> str:
    """
    Serialize a Python object to a TOML string.

    Parameters:
        obj (Any):
            Python object to serialize
        pretty (bool):
            Enable pretty-printed output
        none_value (str | None):
            String representation for None values (e.g. none_value="null" serializes `None` as "null")

    Returns:
        (str):
            TOML-formatted string
    """
    return rtoml.dumps(obj, pretty=pretty, none_value=none_value)


def dump(
    obj: Any,
    file: Path | TextIO | BinaryIO,
    *,
    pretty: bool = False,
    none_value: str | None = "null",
    encoding: str = "utf-8",
) -> int:
    """
    Serialize a Python object and write it to a file or stream.

    Parameters:
        obj (Any):
            Python object to serialize
        file (Path | TextIO | BinaryIO):
            Output target
        pretty (bool):
            Enable pretty-printed output
        none_value (str | None):
            String representation for None values (e.g. none_value="null" serializes `None` as "null")
        encoding (str):
            Text encoding used for file or binary output

    Returns:
        (int):
            Number of characters or bytes written
    """
    s = dumps(obj, pretty=pretty, none_value=none_value)

    # path
    if isinstance(file, Path):
        return file.write_text(s, encoding=encoding)

    # text stream
    if isinstance(file, TextIOBase):
        return file.write(s)

    # binary stream
    if isinstance(file, BufferedIOBase):
        data = s.encode(encoding=encoding)
        return file.write(data)

    raise TypeError(f"invalid file type: {type(file)}")
