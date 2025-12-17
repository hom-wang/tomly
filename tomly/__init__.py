from collections.abc import Iterable
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
    "TomlDict",
]


class TomlDict(dict):
    """
    Enhanced dictionary with dot notation access and nested operations.

    Example:
        >>> data = TomlDict({"database": {"settings": {"port": 5432}}})
        >>> # Access via attributes
        >>> print(data.database.settings.port)  # 5432
        >>> # Modify via attributes
        >>> data.database.settings.ssl = True
        >>> # Convert back to standard dict
        >>> raw_dict = data.to_dict()
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize and recursively wrap nested structures.
        """
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            # Use super().__setitem__ to avoid redundant logic during init
            super().__setitem__(key, self._wrap(value))

    @classmethod
    def _wrap(cls, value: Any) -> Any:
        """
        Recursively wrap dictionaries into TomlDict instances.
        """
        if isinstance(value, dict) and not isinstance(value, cls):
            return cls(value)
        if isinstance(value, list):
            return [cls._wrap(v) for v in value]
        return value

    @classmethod
    def _unwrap(cls, value: Any) -> Any:
        """
        Recursively unwrap TomlDict instances back into standard Python objects.
        """
        if isinstance(value, TomlDict):
            return {k: cls._unwrap(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._unwrap(v) for v in value]
        return value

    def __getattr__(self, key: str) -> Any:
        """
        Map attribute access to dictionary lookup.
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"TomlDict object has no attribute '{key}'") from None

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Allow attribute assignment with auto-wrapping, protecting private attributes.
        """
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key: str) -> None:
        """
        Allow deleting items using attribute syntax.
        """
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"TomlDict object has no attribute '{key}'") from None

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Intercept all data insertion to ensure recursive wrapping.
        """
        super().__setitem__(key, self._wrap(value))

    def get_nested(self, path: str | Iterable[str], default: Any = None, separator: str = ".") -> Any:
        """
        Safely retrieve a value from a deep path without raising errors.
        """
        keys = path.split(separator) if isinstance(path, str) else path

        current = self
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def set_nested(self, path: str | Iterable[str], value: Any, separator: str = ".") -> None:
        """
        Set a value at a deep path, auto-creating intermediate TomlDicts.
        """
        keys = path.split(separator) if isinstance(path, str) else path

        current = self
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = TomlDict()
            current = current[key]
        current[keys[-1]] = value

    def delete_nested(self, path: str, separator: str = ".") -> bool:
        """
        Delete a nested path and return True if successful.
        """
        keys = path.split(separator)
        current = self
        for key in keys[:-1]:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]

        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """
        Deep convert TomlDict back to standard Python dicts.
        """
        return self._unwrap(self)

    def flatten(self, separator: str = ".", parent_key: str = "") -> dict[str, Any]:
        """
        Flatten nested structures into a single-level dictionary.
        Optimized for performance by avoiding redundant object creation.
        """
        result = {}

        def _flatten_recursive(current_item: Any, current_key: str) -> None:
            if isinstance(current_item, dict):
                for key, value in current_item.items():
                    new_key = f"{current_key}{separator}{key}" if current_key else key
                    _flatten_recursive(value, new_key)

            elif isinstance(current_item, list) and current_item and isinstance(current_item[0], dict):
                for i, item in enumerate(current_item):
                    _flatten_recursive(item, f"{current_key}[{i}]")

            else:
                result[current_key] = current_item

        _flatten_recursive(self, parent_key)
        return result


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
