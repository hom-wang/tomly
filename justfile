
@default: venv update-version build test

@venv:
    uv sync --extra dev

@update-version:
    uv run tomly/_version.py

@clear:
    rm -rf dist

@build: clear
    uv build --no-sources

@test:
    uv run tests/test_toml.py

@publish: default
    uv publish --token "$(pass show pypi/token)"
