"""Unit tests for the config module."""

from pathlib import Path

import pytest

from bingomatic.config import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigValidationError,
    get_config_dir,
    get_config_path,
    load_config,
    validate_config,
    load_and_validate_config,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestGetConfigPath:
    """Tests for get_config_path and get_config_dir functions."""

    def test_get_config_dir_returns_home_bingomatic(self):
        """get_config_dir returns ~/.bingomatic/."""
        result = get_config_dir()
        assert result == Path.home() / ".bingomatic"

    def test_get_config_path_returns_config_yaml(self):
        """get_config_path returns ~/.bingomatic/config.yaml."""
        result = get_config_path()
        assert result == Path.home() / ".bingomatic" / "config.yaml"


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_with_valid_yaml(self):
        """load_config successfully parses valid YAML file."""
        config_path = FIXTURES_DIR / "valid_config.yaml"
        config = load_config(config_path)

        assert config["event_name"] == "DevOpsDays Austin 2026"
        assert config["logo_location"] == "/path/to/logo.png"
        assert config["output_directory"] == "/path/to/output"
        assert len(config["bingo_squares"]) == 4

    def test_load_config_with_missing_file(self):
        """load_config raises ConfigFileNotFoundError for missing file."""
        config_path = FIXTURES_DIR / "nonexistent.yaml"

        with pytest.raises(ConfigFileNotFoundError) as exc_info:
            load_config(config_path)

        assert "Config file missing" in str(exc_info.value)

    def test_load_config_with_invalid_yaml(self, tmp_path):
        """load_config raises ConfigError for invalid YAML syntax."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("event_name: [unclosed bracket")

        with pytest.raises(ConfigError) as exc_info:
            load_config(invalid_yaml)

        assert "invalid YAML syntax" in str(exc_info.value)


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_config_with_all_valid_fields(self):
        """validate_config returns empty list for valid config."""
        config = {
            "event_name": "Test Event",
            "logo_location": "/path/to/logo.png",
            "output_directory": "/path/to/output",
            "bingo_squares": ["item1", "item2"],
        }

        errors = validate_config(config)
        assert errors == []

    def test_validate_config_with_missing_required_fields(self):
        """validate_config returns errors for missing required fields."""
        config = {}

        errors = validate_config(config)

        assert len(errors) == 4
        assert "Missing required field: event_name" in errors
        assert "Missing required field: logo_location" in errors
        assert "Missing required field: output_directory" in errors
        assert "Missing required field: bingo_squares" in errors

    def test_validate_config_with_wrong_field_types(self):
        """validate_config returns errors for wrong field types."""
        config = {
            "event_name": 123,
            "logo_location": ["not", "a", "string"],
            "output_directory": {"wrong": "type"},
            "bingo_squares": "not an array",
        }

        errors = validate_config(config)

        assert len(errors) == 4
        assert any("event_name" in e and "str" in e for e in errors)
        assert any("logo_location" in e and "str" in e for e in errors)
        assert any("output_directory" in e and "str" in e for e in errors)
        assert any("bingo_squares" in e and "list" in e for e in errors)

    def test_validate_config_with_empty_bingo_squares(self):
        """validate_config returns error for empty bingo_squares array."""
        config = {
            "event_name": "Test Event",
            "logo_location": "/path/to/logo.png",
            "output_directory": "/path/to/output",
            "bingo_squares": [],
        }

        errors = validate_config(config)

        assert len(errors) == 1
        assert "must contain at least one item" in errors[0]

    def test_validate_config_with_empty_string_fields(self):
        """validate_config returns errors for empty string fields."""
        config = {
            "event_name": "",
            "logo_location": "  ",
            "output_directory": "\t",
            "bingo_squares": ["item1"],
        }

        errors = validate_config(config)

        assert len(errors) == 3
        assert any("event_name" in e and "non-empty" in e for e in errors)
        assert any("logo_location" in e and "non-empty" in e for e in errors)
        assert any("output_directory" in e and "non-empty" in e for e in errors)


class TestValidateConfigMultiError:
    """Tests for multi-error collection in validate_config."""

    def test_multiple_validation_errors_collected(self):
        """validate_config collects multiple errors before returning."""
        config = {
            "event_name": "",
            "bingo_squares": "not an array",
        }

        errors = validate_config(config)

        assert len(errors) >= 3
        assert any("event_name" in e for e in errors)
        assert any("logo_location" in e for e in errors)
        assert any("bingo_squares" in e for e in errors)


class TestConfigValidationError:
    """Tests for ConfigValidationError formatting."""

    def test_single_error_format(self):
        """ConfigValidationError with single error formats correctly."""
        error = ConfigValidationError(["Missing required field: event_name"])

        assert str(error) == "Missing required field: event_name"

    def test_multiple_error_format(self):
        """ConfigValidationError with multiple errors formats correctly."""
        error = ConfigValidationError([
            "Missing required field: event_name",
            "Field 'bingo_squares' must be a list, got str",
        ])

        error_str = str(error)
        assert "Configuration validation failed with 2 errors:" in error_str
        assert "Missing required field: event_name" in error_str
        assert "bingo_squares" in error_str


class TestLoadAndValidateConfig:
    """Tests for load_and_validate_config function."""

    def test_load_and_validate_with_valid_config(self):
        """load_and_validate_config returns config dict for valid file."""
        config_path = FIXTURES_DIR / "valid_config.yaml"
        config = load_and_validate_config(config_path)

        assert config["event_name"] == "DevOpsDays Austin 2026"

    def test_load_and_validate_with_missing_file(self):
        """load_and_validate_config raises ConfigFileNotFoundError."""
        config_path = FIXTURES_DIR / "nonexistent.yaml"

        with pytest.raises(ConfigFileNotFoundError):
            load_and_validate_config(config_path)

    def test_load_and_validate_with_invalid_config(self, tmp_path):
        """load_and_validate_config raises ConfigValidationError for invalid config."""
        invalid_config = tmp_path / "invalid_config.yaml"
        invalid_config.write_text("event_name: ''")

        with pytest.raises(ConfigValidationError) as exc_info:
            load_and_validate_config(invalid_config)

        assert len(exc_info.value.errors) >= 1
