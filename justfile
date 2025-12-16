
@default: venv update-version build

@venv:
    uv sync --extra dev

@update-version:
    uv run tomly/_version.py

@clear:
    rm -rf dist

@build: clear
    uv build --no-sources

@publish: default
    uv publish --token "$(pass show pypi/token)"
