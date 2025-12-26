import os
import re
from collections.abc import Iterable, Mapping
from io import BufferedIOBase, TextIOBase
from pathlib import Path
from typing import Any, BinaryIO, TextIO

import rtoml

from ._version import __version__  # noqa: F401

__all__ = [
    "TomlParsingError",
    "TomlSerializationError",
    "load",
    "loads",
    "dumps",
    "dump",
    "sanitize",
    "DataDict",
]

TomlParsingError = rtoml.TomlParsingError
TomlSerializationError = rtoml.TomlSerializationError


class DataDict(dict):
    """
    Enhanced dictionary with dot notation access and nested operations.

    Example:
        >>> data = DataDict({"database": {"settings": {"port": 5432}}})
        >>> # Access via attributes
        >>> print(data.database.settings.port)  # 5432
        >>> # Modify via attributes
        >>> data.database.settings.ssl = True
        >>> # Convert back to standard dict
        >>> raw_dict = data.to_dict()
    """

    # Class-level cache and constants
    _BASE_DIR = None
    _ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::([^}]*))?\}", re.IGNORECASE)
    # __slots__ = ("_frozen", "_coerce_mapping")  # Allow _frozen attribute

    def __init__(self, *args, interpolate_env: bool = False, coerce_mapping: bool = True, **kwargs) -> None:
        """
        Initialize and recursively wrap nested structures.

        Args:
            interpolate_env (bool):
                If True, expand environment variables in string values, Syntax: `${VAR_NAME:default_value}` or `${VAR_NAME}`
        """
        super().__init__(*args, **kwargs)

        self._frozen: bool = False
        self._coerce_mapping: bool = coerce_mapping

        # Wrap nested structures efficiently
        for key, value in self.items():
            wrapped = self._wrap(value, interpolate_env=interpolate_env)
            if wrapped is not value:
                super().__setitem__(key, wrapped)

    def __getattr__(self, key: str) -> Any:
        """Map attribute access to dictionary lookup."""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"DataDict object has no attribute '{key}'") from None

    def __setattr__(self, key: str, value: Any) -> None:
        """Allow attribute assignment with auto-wrapping, protecting private attributes."""
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key: str) -> None:
        """Allow deleting items using attribute syntax."""
        self._check_frozen()
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"DataDict object has no attribute '{key}'") from None

    def __setitem__(self, key: Any, value: Any) -> None:
        """Intercept all data insertion to ensure recursive wrapping."""
        self._check_frozen()

        if self._coerce_mapping:
            value = self._wrap(value)

        super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        """Delete item with frozen check."""
        self._check_frozen()
        super().__delitem__(key)

    def __dir__(self) -> list[str]:
        """Return the list of attributes for the object."""
        if DataDict._BASE_DIR is None:
            DataDict._BASE_DIR = frozenset(super().__dir__())
        keys = {k for k in self if isinstance(k, str) and k.isidentifier()}
        return sorted(DataDict._BASE_DIR | keys)

    @classmethod
    def _wrap(cls, value: Any, *, interpolate_env: bool = False) -> Any:
        """
        Recursively wrap dictionaries and sequences into DataDict instances.

        Args:
            value (Any):
                The data structure or scalar value to wrap.
            interpolate_env (bool):
                If True, strings containing environment variable patterns will be expanded (default: False).

        Returns:
            Any:
                A DataDict if the input was a mapping, a list of wrapped items if the input
                was a list, or the original value if no wrapping was required.
        """
        # Interpolate environment variables in strings first
        if interpolate_env and isinstance(value, str):
            value = cls._interpolate_env(value)

        value_type = type(value)

        # Fast path: exact dict type (most common case)
        if value_type is dict:
            return cls(value, interpolate_env=interpolate_env)

        # Already a DataDict, return as-is
        if value_type is cls:
            return value

        # Handle lists
        if value_type is list:
            if not value:  # Empty list early return
                return value
            # Wrap list if it contains dicts or needs env expansion
            if interpolate_env or any(isinstance(v, dict) for v in value):
                return [cls._wrap(v, interpolate_env=interpolate_env) for v in value]
            return value

        # Slow path: dict subclasses (less common)
        if isinstance(value, dict):
            return cls(value, interpolate_env=interpolate_env)

        # Default: return as-is (int, float, str, bool, None, etc.)
        return value

    @classmethod
    def _unwrap(cls, value: Any) -> Any:
        """
        Recursively convert DataDict instances back to standard Python dictionaries.

        Args:
            value (Any):
                The DataDict or structure containing DataDicts to be converted.

        Returns:
            Any:
                Standard Python dictionaries and lists with all DataDict wrappers removed.
        """
        value_type = type(value)

        if value_type is cls or isinstance(value, dict):
            return {k: cls._unwrap(v) for k, v in value.items()}

        if value_type is list:
            if value and any(isinstance(v, dict | list) for v in value):
                return [cls._unwrap(v) for v in value]
            return value

        return value

    @classmethod
    def _interpolate_env(cls, value: str) -> str:
        """
        Expand environment variables within a string using a defined pattern.

        Supports two syntaxes:
        - `${VAR_NAME}` - replaced with env var or kept as-is if not found
        - `${VAR_NAME:<DEFAULT>}` - replaced with env var or default value

        Examples:
            >>> os.environ["DB_HOST"] = "localhost"
            >>> DataDict._interpolate_env("${DB_HOST}")
            'localhost'
            >>> DataDict._interpolate_env("${MISSING:default}")
            'default'

        Args:
            value (str):
                The string potentially containing environment variable placeholders.

        Returns:
            str:
                The processed string with variables replaced by their system values or
                defaults. If no match is found and no default is provided, the original
                placeholder is preserved.
        """
        if not value or "$" not in value:
            return value

        def _replacer(match):
            var_name = match.group(1)
            default = match.group(2) if match.lastindex >= 2 else None

            env_value = os.environ.get(var_name)

            if env_value is not None:
                return env_value
            elif default is not None:
                return default
            else:
                return match.group(0)  # Keep original if no env var and no default

        return cls._ENV_PATTERN.sub(_replacer, value)

    @staticmethod
    def _split_path(path: str | Iterable[str], separator: str) -> list[str]:
        """
        Normalize various path formats into a consistent list of keys.

        Args:
            path (str | Iterable[str]):
                A string delimited by the separator or an iterable of individual keys.
            separator (str):
                The character used to split the path if it is provided as a string.

        Returns:
            list[str]:
                A flat list of string keys representing the hierarchical path.
        """
        if isinstance(path, str):
            return path.split(separator) if path else []
        return list(path)

    def _check_frozen(self) -> None:
        """Verify the mutation state of the DataDict before performing write operations."""
        if self._frozen:
            raise TypeError("Cannot modify a frozen DataDict")

    def _freeze_value(self, value: Any) -> None:
        if type(value) is DataDict:
            value.freeze()
        elif isinstance(value, list | tuple | set):
            for item in value:
                self._freeze_value(item)

    def clear(self) -> None:
        """Clear all items with frozen check."""
        self._check_frozen()
        super().clear()

    def pop(self, *args) -> Any:
        """Pop item with frozen check."""
        self._check_frozen()
        return super().pop(*args)

    def popitem(self) -> tuple[Any, Any]:
        """Pop item with frozen check."""
        self._check_frozen()
        return super().popitem()

    def update(self, *args, **kwargs) -> None:
        """Update with frozen check and proper value wrapping."""
        self._check_frozen()

        if not self._coerce_mapping:
            super().update(*args, **kwargs)
            return

        if len(args) > 1:
            raise TypeError(f"update expected at most 1 argument, got {len(args)}")

        if args:
            other = args[0]
            items = getattr(other, "items", None)
            if callable(items):
                for k, v in items():
                    self[k] = v
            else:
                for k, v in other:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def setdefault(self, key: Any, default: Any = None) -> Any:
        """Set default with frozen check and proper value wrapping."""
        self._check_frozen()

        if not self._coerce_mapping:
            return super().setdefault(key, default)

        if key not in self:
            self[key] = default  # goes through __setitem__ -> wrapping
        return self[key]

    def get_nested(self, path: str | Iterable[str], default: Any = None, *, separator: str = ".") -> Any:
        """
        Safely retrieve a value from a deep path without raising errors.

        Args:
            path (str | Iterable[str]):
                Dot-separated string or iterable of keys representing the path.
            default (Any):
                Value to return if any key in the path does not exist (default: None).
            separator (str):
                Character used to split the path string (default: ".").

        Returns:
            Any:
                The value at the specified path, or the default value if the path is invalid.
        """
        if isinstance(path, str):
            if not path:
                return self
            keys = path.split(separator)
        else:
            keys = list(path)

        try:
            current = self
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def set_nested(self, path: str | Iterable[str], value: Any, *, separator: str = ".") -> None:
        """
        Set a value at a deep path, auto-creating intermediate DataDicts as needed.

        Args:
            path (str | Iterable[str]):
                Dot-separated string or iterable of keys where the value should be set.
            value (Any):
                The value to store at the specified path; will be auto-wrapped.
            separator (str):
                Character used to split the path string (default: ".").
        """
        if isinstance(path, str):
            if not path:
                raise ValueError("Path must not be empty")
            keys = path.split(separator)
        else:
            keys = list(path)
            if not keys:
                raise ValueError("Path must not be empty")

        current = self
        for key in keys[:-1]:
            next_node = current.get(key)
            if next_node is None or not isinstance(next_node, dict):
                next_node = DataDict()
                current[key] = next_node
            current = next_node

        current[keys[-1]] = value

    def delete_nested(self, path: str | Iterable[str], *, separator: str = ".") -> bool:
        """
        Delete a nested path and return a success status.

        Args:
            path (str | Iterable[str]):
                Dot-separated string or iterable of keys to be removed.
            separator (str):
                Character used to split the path string (default: ".").

        Returns:
            bool:
                True if the path existed and was successfully deleted, False otherwise.
        """
        self._check_frozen()

        keys = self._split_path(path, separator)
        if not keys:
            return False

        current = self
        try:
            for key in keys[:-1]:
                current = current[key]
            del current[keys[-1]]
            return True
        except (KeyError, TypeError):
            return False

    def to_dict(self) -> dict[str, Any]:
        """
        Deeply convert the DataDict and all its nested children back to standard Python dicts.

        Returns:
            dict[str, Any]:
                A standard Python dictionary representing the current data structure.
        """
        return self._unwrap(self)

    def flatten(self, *, separator: str = ".", parent_key: str = "", expand_lists: bool = False) -> dict[str, Any]:
        """
        Flatten nested structures into a single-level dictionary.

        Args:
            separator (str):
                String separator for nested keys (default: ".").
            parent_key (str):
                Prefix to be prepended to all generated keys (default: "").
            expand_lists (bool):
                Whether to expand list items using [index] notation (e.g., "users[0]").

        Returns:
            dict[str, Any]:
                A new flat dictionary with dot-notation keys.
        """
        result = {}
        stack = [(self, parent_key)]

        while stack:
            item, key = stack.pop()

            if isinstance(item, Mapping):
                items = list(item.items())
                for k, v in reversed(items):
                    new_key = f"{key}{separator}{k}" if key else str(k)
                    stack.append((v, new_key))
                continue

            if expand_lists and isinstance(item, list):
                for i in range(len(item) - 1, -1, -1):
                    stack.append((item[i], f"{key}[{i}]"))

                if not item and key:
                    result[key] = []
                continue

            if key:
                result[key] = item

        return result

    def merge(self, other: Mapping[str, Any]) -> None:
        """
        Recursively merge another mapping into this DataDict.

        Args:
            other (Mapping[str, Any]):
                The source mapping to merge into the current instance.
        """
        for key, value in other.items():
            existing = self.get(key)
            if existing is not None and isinstance(existing, DataDict) and isinstance(value, Mapping):
                existing.merge(value)
            else:
                self[key] = value

    def freeze(self) -> "DataDict":
        """
        Recursively freeze the DataDict and all nested DataDicts to prevent modifications.

        Returns:
            DataDict:
                The current instance (self) after being frozen.
        """
        if self._frozen:
            return self

        self._frozen = True
        for v in self.values():
            self._freeze_value(v)

        return self


def sanitize(obj: Any) -> Any:
    """
    Recursively convert types that are not TOML-compatible into compatible equivalents.

    Current conversions:
    - pathlib.Path -> str
    - set -> list
    - tuple -> list
    - dict -> recursively sanitized dict
    - list -> recursively sanitized list

    Args:
        obj (Any):
            Object to sanitize

    Returns:
        Any:
            Sanitized object
    """
    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}

    if isinstance(obj, list | tuple | set):
        return [sanitize(v) for v in obj]

    return obj


def loads(
    toml: str,
    *,
    none_value: str | None = None,
) -> dict[str, Any]:
    """
    Parse TOML content from a string.

    Args:
        toml (str):
            TOML-formatted string
        none_value (str | None):
            String value to be interpreted as None (e.g. none_value="null" maps TOML "null" to `None`)

    Returns:
        dict[str, Any]:
            Parsed TOML data as a dictionary
    """
    return rtoml.loads(toml, none_value=none_value)


def load(
    toml: str | Path | TextIO | BinaryIO,
    *,
    none_value: str | None = None,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """
    Load and parse TOML content from various input sources.

    Supported inputs:
        - File path
        - Text stream
        - Binary stream
        - Raw TOML string

    Args:
        toml (str | Path | TextIO | BinaryIO):
            TOML source
        none_value (str | None):
            String value to be interpreted as None (e.g. none_value="null" maps TOML "null" to `None`)
        encoding (str):
            Text encoding used for file or binary input

    Returns:
        dict[str, Any]:
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

    # else: assume it's already a string

    return loads(toml, none_value=none_value)


def dumps(
    obj: Any,
    *,
    pretty: bool = False,
    none_value: str | None = "null",
    sanitize: bool = False,
) -> str:
    """
    Serialize a Python object to a TOML string.

    Args:
        obj (Any):
            Python object to serialize
        pretty (bool):
            Enable pretty-printed output
        none_value (str | None):
            String representation for None values (e.g. none_value="null" serializes `None` as "null")
        sanitize (bool):
            Convert types that are not strictly TOML-compatible (default: False)

    Returns:
        str:
            TOML-formatted string
    """
    if type(obj) is DataDict:
        obj = obj.to_dict()

    # Sanitize object to handle non-serializable types like Path
    if sanitize:
        obj = globals()["sanitize"](obj)

    return rtoml.dumps(obj, pretty=pretty, none_value=none_value)


def dump(
    obj: Any,
    file: Path | TextIO | BinaryIO,
    *,
    pretty: bool = False,
    none_value: str | None = "null",
    encoding: str = "utf-8",
    sanitize: bool = False,
) -> int:
    """
    Serialize a Python object and write it to a file or stream.

    Args:
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
        sanitize (bool):
            Convert types that are not strictly TOML-compatible (default: False)

    Returns:
        int:
            Number of characters or bytes written
    """
    s = dumps(obj, pretty=pretty, none_value=none_value, sanitize=sanitize)

    # path
    if isinstance(file, Path):
        return file.write_text(s, encoding=encoding)

    # text stream
    if isinstance(file, TextIOBase):
        return file.write(s)

    # binary stream
    if isinstance(file, BufferedIOBase):
        return file.write(s.encode(encoding=encoding))

    raise TypeError(f"invalid file type: {type(file)}")
