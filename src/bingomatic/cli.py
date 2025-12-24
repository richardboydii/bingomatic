"""Command-line interface for Bingomatic."""

import sys

import click

from bingomatic.config import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigValidationError,
    load_and_validate_config,
)


@click.group()
@click.version_option()
def main() -> None:
    """Bingomatic - A bingo card generator for conferences like DevOpsDays."""
    pass


@main.command()
def validate() -> None:
    """Validate the configuration file."""
    try:
        load_and_validate_config()
        click.echo("Configuration valid.")
        sys.exit(0)
    except ConfigFileNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except ConfigValidationError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except ConfigError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
