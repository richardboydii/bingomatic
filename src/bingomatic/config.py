"""Configuration loading and validation for Bingomatic."""

from pathlib import Path
from typing import Any

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfigFileNotFoundError(ConfigError):
    """Exception raised when config file is not found."""

    pass


class ConfigValidationError(ConfigError):
    """Exception raised when config validation fails."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(self._format_errors())

    def _format_errors(self) -> str:
        if len(self.errors) == 1:
            return self.errors[0]
        return f"Configuration validation failed with {len(self.errors)} errors:\n" + "\n".join(
            f"  - {error}" for error in self.errors
        )


def get_config_dir() -> Path:
    """Return the path to the configuration directory.

    Returns:
        Path to ~/.bingomatic/
    """
    return Path.home() / ".bingomatic"


def get_config_path() -> Path:
    """Return the path to the configuration file.

    Returns:
        Path to ~/.bingomatic/config.yaml
    """
    return get_config_dir() / "config.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load and parse the YAML configuration file.

    Args:
        config_path: Optional path to config file. Defaults to ~/.bingomatic

    Returns:
        Dictionary containing the parsed configuration

    Raises:
        ConfigFileNotFoundError: If the config file doesn't exist
        ConfigError: If the YAML syntax is invalid
    """
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        raise ConfigFileNotFoundError(
            "Config file missing, please create it using the template and README instructions."
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Config file has invalid YAML syntax: {e}")

    if config is None:
        config = {}

    return config


def validate_config(config: dict[str, Any]) -> list[str]:
    """Validate the configuration dictionary.

    Collects all validation errors before returning.

    Args:
        config: Dictionary containing the configuration

    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []

    # Required fields and their expected types
    required_fields = {
        "event_name": str,
        "logo_location": str,
        "output_directory": str,
        "bingo_squares": list,
    }

    for field, expected_type in required_fields.items():
        if field not in config:
            errors.append(f"Missing required field: {field}")
        else:
            value = config[field]
            actual_type = type(value).__name__

            if not isinstance(value, expected_type):
                errors.append(
                    f"Field '{field}' must be a {expected_type.__name__}, got {actual_type}"
                )
            elif expected_type == str and not value.strip():
                errors.append(f"Field '{field}' must be a non-empty string")
            elif expected_type == list and len(value) == 0:
                errors.append(f"Field 'bingo_squares' must contain at least one item")

    return errors


def load_and_validate_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load and validate the configuration file.

    Args:
        config_path: Optional path to config file. Defaults to ~/.bingomatic

    Returns:
        Dictionary containing the validated configuration

    Raises:
        ConfigFileNotFoundError: If the config file doesn't exist
        ConfigError: If the YAML syntax is invalid
        ConfigValidationError: If validation fails
    """
    config = load_config(config_path)
    errors = validate_config(config)

    if errors:
        raise ConfigValidationError(errors)

    return config
