"""
Environment variable interpolation tests for DataDict.
Tests the ${VAR_NAME:default} pattern expansion.
"""

from tomly import DataDict

# ==============================================================
# Test environment variable expansion functionality.
# ==============================================================


def test_interpolation_disabled_by_default(monkeypatch):
    """
    Test that interpolation is disabled by default.
    """
    monkeypatch.setenv("TEST_VAR", "value")
    dd = DataDict(
        {
            "key": "${TEST_VAR}",
        }
    )
    assert dd.key == "${TEST_VAR}"  # Should not interpolate


def test_basic_env_var_expansion(monkeypatch):
    """
    Test basic environment variable expansion.
    """
    monkeypatch.setenv("DB_HOST", "localhost")
    dd = DataDict(
        {
            "host": "${DB_HOST}",
        },
        interpolate_env=True,
    )
    assert dd.host == "localhost"


def test_env_var_with_default_value(monkeypatch):
    """
    Test environment variable with default value syntax.
    """
    monkeypatch.delenv("MISSING_VAR", raising=False)
    dd = DataDict(
        {
            "port": "${MISSING_VAR:8080}",
        },
        interpolate_env=True,
    )
    assert dd.port == "8080"


def test_env_var_without_default_preserved(monkeypatch):
    """
    Test that missing env vars without defaults are preserved.
    """
    monkeypatch.delenv("MISSING_VAR", raising=False)
    dd = DataDict(
        {
            "key": "${MISSING_VAR}",
        },
        interpolate_env=True,
    )
    assert dd.key == "${MISSING_VAR}"


def test_env_var_takes_precedence_over_default(monkeypatch):
    """
    Test that actual env var takes precedence over default.
    """
    monkeypatch.setenv("MY_VAR", "actual")
    dd = DataDict(
        {
            "key": "${MY_VAR:default}",
        },
        interpolate_env=True,
    )
    assert dd.key == "actual"


def test_multiple_env_vars_in_string(monkeypatch):
    """
    Test multiple environment variables in one string.
    """
    monkeypatch.setenv("HOST", "example.com")
    monkeypatch.setenv("PORT", "443")
    dd = DataDict(
        {
            "url": "https://${HOST}:${PORT}/api",
        },
        interpolate_env=True,
    )
    assert dd.url == "https://example.com:443/api"


def test_nested_dict_interpolation(monkeypatch):
    """
    Test interpolation in nested dictionaries.
    """
    monkeypatch.setenv("DB_HOST", "192.168.1.1")
    monkeypatch.setenv("DB_PORT", "5432")

    dd = DataDict(
        {
            "database": {
                "host": "${DB_HOST}",
                "port": "${DB_PORT:3306}",
                "user": "${DB_USER:admin}",
            }
        },
        interpolate_env=True,
    )

    assert dd.database.host == "192.168.1.1"
    assert dd.database.port == "5432"
    assert dd.database.user == "admin"


def test_list_interpolation(monkeypatch):
    """
    Test interpolation in list values.
    """
    monkeypatch.setenv("SERVER1", "host1.com")
    monkeypatch.setenv("SERVER2", "host2.com")

    dd = DataDict(
        {
            "servers": [
                "${SERVER1}",
                "${SERVER2}",
                "${SERVER3:fallback.com}",
            ],
        },
        interpolate_env=True,
    )

    assert dd.servers[0] == "host1.com"
    assert dd.servers[1] == "host2.com"
    assert dd.servers[2] == "fallback.com"


def test_dict_in_list_interpolation(monkeypatch):
    """
    Test interpolation in dicts within lists.
    """
    monkeypatch.setenv("HOST1", "server1")

    dd = DataDict(
        {
            "configs": [
                {
                    "host": "${HOST1}",
                },
                {
                    "host": "${HOST2:server2}",
                },
            ]
        },
        interpolate_env=True,
    )

    assert dd.configs[0].host == "server1"
    assert dd.configs[1].host == "server2"


def test_empty_string_env_var(monkeypatch):
    """
    Test environment variable set to empty string.
    """
    monkeypatch.setenv("EMPTY_VAR", "")
    dd = DataDict(
        {
            "key": "${EMPTY_VAR:default}",
        },
        interpolate_env=True,
    )
    assert dd.key == ""  # Empty string is a valid value


def test_special_characters_in_default(monkeypatch):
    """
    Test default values with special characters.
    """
    dd = DataDict(
        {
            "path": "${MISSING:/usr/local/bin}",
            "url": "${MISSING:http://example.com:8080}",
            "special": "${MISSING:value:with:colons}",
        },
        interpolate_env=True,
    )

    assert dd.path == "/usr/local/bin"
    assert dd.url == "http://example.com:8080"
    assert dd.special == "value:with:colons"


def test_case_sensitive_var_names(monkeypatch):
    """
    Test that variable names are case-sensitive.
    """
    monkeypatch.setenv("MyVar", "lowercase")
    monkeypatch.setenv("MYVAR", "uppercase")

    dd = DataDict(
        {
            "lower": "${MyVar}",
            "upper": "${MYVAR}",
        },
        interpolate_env=True,
    )

    assert dd.lower == "lowercase"
    assert dd.upper == "uppercase"


def test_non_string_values_not_interpolated(monkeypatch):
    """
    Test that non-string values are not processed.
    """
    monkeypatch.setenv("NUM", "42")

    dd = DataDict(
        {
            "int": 123,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
        },
        interpolate_env=True,
    )

    assert dd.int == 123
    assert dd.float == 3.14
    assert dd.bool is True
    assert dd.none is None
    assert dd.list == [1, 2, 3]


def test_dollar_sign_without_braces_not_interpolated(monkeypatch):
    """
    Test that $ without proper syntax is not interpolated.
    """
    monkeypatch.setenv("VAR", "value")

    dd = DataDict(
        {
            "price": "$100",
            "path": "/var/$VAR/data",
            "incomplete": "${",
            "no_close": "${VAR",
        },
        interpolate_env=True,
    )

    assert dd.price == "$100"
    assert dd.path == "/var/$VAR/data"
    assert dd.incomplete == "${"
    assert dd.no_close == "${VAR"


def test_escaped_dollar_signs():
    """
    Test double dollar signs (escaped).
    """
    dd = DataDict(
        {
            "escaped": "$${NOT_A_VAR}",
        },
        interpolate_env=True,
    )
    assert dd.escaped == "$${NOT_A_VAR}"


def test_empty_var_name():
    """
    Test empty variable name in pattern.
    """
    dd = DataDict(
        {
            "key": "${}:default}",
        },
        interpolate_env=True,
    )
    assert dd.key == "${}:default}"


def test_whitespace_in_var_name(monkeypatch):
    """
    Test that whitespace in var names is not matched.
    """
    monkeypatch.setenv("VAR WITH SPACE", "value")
    dd = DataDict(
        {
            "key": "${VAR WITH SPACE}",
        },
        interpolate_env=True,
    )
    # Should not match due to pattern restriction
    assert dd.key == "${VAR WITH SPACE}"


def test_numeric_var_names(monkeypatch):
    """
    Test environment variables with numbers.
    """
    monkeypatch.setenv("VAR123", "value1")
    monkeypatch.setenv("123VAR", "value2")

    dd = DataDict(
        {
            "alpha_num": "${VAR123}",
            "num_alpha": "${123VAR}",
        },
        interpolate_env=True,
    )

    assert dd.alpha_num == "value1"
    assert dd.num_alpha == "value2"


def test_underscore_in_var_names(monkeypatch):
    """
    Test environment variables with underscores.
    """
    monkeypatch.setenv("MY_VAR_NAME", "underscore_value")
    dd = DataDict(
        {
            "key": "${MY_VAR_NAME}",
        },
        interpolate_env=True,
    )
    assert dd.key == "underscore_value"


def test_complex_real_world_config(monkeypatch):
    """
    Test a realistic configuration scenario.
    """
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DB_HOST", "db.example.com")
    monkeypatch.setenv("REDIS_PORT", "6379")

    dd = DataDict(
        {
            "app": {
                "environment": "${APP_ENV:development}",
                "debug": "${DEBUG:false}",
                "url": "https://${DOMAIN:localhost}:${PORT:8000}",
            },
            "database": {
                "host": "${DB_HOST}",
                "port": "${DB_PORT:5432}",
                "name": "${DB_NAME:myapp}",
            },
            "cache": {
                "host": "${REDIS_HOST:localhost}",
                "port": "${REDIS_PORT}",
            },
        },
        interpolate_env=True,
    )

    assert dd.app.environment == "production"
    assert dd.app.debug == "false"
    assert dd.app.url == "https://localhost:8000"
    assert dd.database.host == "db.example.com"
    assert dd.database.port == "5432"
    assert dd.database.name == "myapp"
    assert dd.cache.host == "localhost"
    assert dd.cache.port == "6379"


def test_interpolation_performance_with_no_patterns():
    """
    Test that interpolation doesn't slow down strings without patterns.
    """
    dd = DataDict(
        {
            "plain1": "no variables here",
            "plain2": "another plain string",
            "nested": {
                "plain3": "yet another",
                "plain4": "and one more",
            },
        },
        interpolate_env=True,
    )

    assert dd.plain1 == "no variables here"
    assert dd.plain2 == "another plain string"
    assert dd.nested.plain3 == "yet another"
    assert dd.nested.plain4 == "and one more"
