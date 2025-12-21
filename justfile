
@default: venv update-version build test

@venv:
    uv sync --extra dev
    # uv sync --python 3.12 --extra dev

@update-version:
    uv run tomly/_version.py

@clear:
    rm -rf dist

@build: clear
    uv build --no-sources

@test:
    # uv sync --python 3.10 --extra dev
    # uv run pytest --cov=tomly

    # uv sync --python 3.11 --extra dev
    # uv run pytest --cov=tomly

    uv sync --python 3.12 --extra dev
    uv run pytest --cov=tomly

    # uv sync --python 3.13 --extra dev
    # uv run pytest --cov=tomly

    # uv sync --python 3.14 --extra dev
    # uv run pytest --cov=tomly

    coverage report -m
    coverage html -d artifacts/htmlcov
    open artifacts/htmlcov/index.html

@publish: default
    uv publish --token "$(pass show pypi/token)"
