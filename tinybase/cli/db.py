"""Database management CLI commands."""

from typing import Annotated, Optional

import typer

# Create db subcommand group
db_app = typer.Typer(
    name="db",
    help="Database management commands",
)


@db_app.command("migrate")
def db_migrate(
    message: Annotated[
        Optional[str],
        typer.Option("--message", "-m", help="Migration message")
    ] = None,
) -> None:
    """
    Generate a new migration based on model changes.
    
    Compares the current models to the database and generates a migration
    script with the detected changes.
    """
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    
    if message:
        command.revision(alembic_cfg, message=message, autogenerate=True)
    else:
        command.revision(alembic_cfg, message="auto migration", autogenerate=True)
    
    typer.echo("Migration created successfully")


@db_app.command("upgrade")
def db_upgrade(
    revision: Annotated[
        str,
        typer.Argument(help="Revision target (default: head)")
    ] = "head",
) -> None:
    """
    Apply database migrations.
    
    Upgrades the database to the specified revision (default: latest).
    """
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, revision)
    typer.echo(f"Database upgraded to {revision}")


@db_app.command("downgrade")
def db_downgrade(
    revision: Annotated[
        str,
        typer.Argument(help="Revision target")
    ] = "-1",
) -> None:
    """
    Revert database migrations.
    
    Downgrades the database to the specified revision.
    Use "-1" to go back one revision.
    """
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    typer.echo(f"Database downgraded to {revision}")


@db_app.command("history")
def db_history() -> None:
    """
    Show migration history.
    
    Lists all migrations and their status.
    """
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.history(alembic_cfg)


@db_app.command("current")
def db_current() -> None:
    """
    Show current database revision.
    """
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.current(alembic_cfg)

