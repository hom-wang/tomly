# tomly

[![PyPI version](https://img.shields.io/pypi/v/tomly.svg)](https://pypi.org/project/tomly/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**tomly** is a lightweight wrapper around `rtoml`, designed to provide `tomli`/`tomllib` compatible behavior while offering enhanced convenience methods for intuitive data access.

## Key Features

-   🎯 **Dot Notation**: Access and modify nested dictionary keys as object attributes (e.g., `config.db.port`).
-   🌍 **Environment Interpolation**: Automatically expand `${VAR_NAME:default}` patterns within strings during loading.
-   🌳 **Nested Path Operations**: Safely get, set, or delete deep values using dot-separated strings or iterables.
-   🔒 **Immutability (Freeze)**: Protect your configuration from accidental runtime changes.
-   🥞 **Flattening**: Convert nested structures into a single-level dictionary for environment variables or logging.
-   ⚡ **High Performance**: Built on top of `rtoml` (Rust-powered) for rapid parsing and serialization.

## Installation

```bash
pip install tomly
```

## Quick Start

### 1. Basic Loading & Attribute Access

```python
import tomly as toml
from tomly import DataDict

toml_data = """
[server]
host = "127.0.0.1"
port = 8080
"""

# Parse and wrap into DataDict
config = DataDict(toml.loads(toml_data))

# Access via dot notation
print(config.server.host)  # "127.0.0.1"
config.server.port = 9000   # Set values like an object

```

### 2. Environment Variable Interpolation

```python
import os
from tomly import DataDict

os.environ["APP_ENV"] = "production"

# DataDict can resolve ${VAR_NAME} or ${VAR_NAME:default}
data = {"env": "${APP_ENV:dev}", "debug": "${DEBUG:false}"}
config = DataDict(data, interpolate_env=True)

print(config.env) # "production"
print(config.debug) # "false" (using default value)
```

### 3. Deep Path Manipulation

```python
from tomly import DataDict

config = DataDict()

# Set values at deep paths (auto-creates intermediate dicts)
config.set_nested("app.services.auth.timeout", 30)

# Safe retrieval without KeyErrors
timeout = config.get_nested("app.services.auth.timeout", default=60)

# Delete a nested structure
config.delete_nested("app.services.auth")
```

### 4. Read-only Configuration

```python
from tomly import DataDict

config = DataDict({"api": {"version": "v1"}})
config.freeze()

# This will raise a TypeError
config.api.version = "v2"
```
