
@default: venv update-version build test

@venv:
    uv sync --group dev
    # uv sync --python 3.12 --group dev

@update-version:
    uv run tomly/_version.py

@clear:
    rm -rf dist

@build: clear
    uv build --no-sources

@test:
    uv run --python 3.10 pytest --cov=tomly
    uv run --python 3.11 pytest --cov=tomly
    uv run --python 3.13 pytest --cov=tomly
    uv run --python 3.14 pytest --cov=tomly

    uv run --python 3.12 pytest --cov=tomly

    uv run coverage report -m
    uv run coverage html -d artifacts/htmlcov
    open artifacts/htmlcov/index.html

@publish: default
    uv publish --token "$(pass show pypi/token)"
