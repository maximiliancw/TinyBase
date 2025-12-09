"""
TinyBase CLI application.

Provides commands for:
- init: Initialize a new TinyBase instance
- serve: Start the TinyBase server
- functions new: Create a new function boilerplate
- functions deploy: Deploy functions to a remote server
- admin add: Create or update an admin user
- extensions install/uninstall/list/enable/disable: Manage extensions
"""

import re
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from tinybase.version import __version__

# Create CLI app
app = typer.Typer(
    name="tinybase",
    help="TinyBase - A lightweight BaaS framework for Python developers",
    add_completion=False,
)

# Create functions subcommand group
functions_app = typer.Typer(
    name="functions",
    help="Function management commands",
)
app.add_typer(functions_app, name="functions")

# Create db subcommand group
db_app = typer.Typer(
    name="db",
    help="Database management commands",
)
app.add_typer(db_app, name="db")

# Create admin subcommand group
admin_app = typer.Typer(
    name="admin",
    help="Admin user management commands",
)
app.add_typer(admin_app, name="admin")

# Create extensions subcommand group
extensions_app = typer.Typer(
    name="extensions",
    help="Extension management commands",
)
app.add_typer(extensions_app, name="extensions")


# =============================================================================
# Helper Functions
# =============================================================================


def snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def create_default_toml() -> str:
    """Generate default tinybase.toml content."""
    return '''# TinyBase Configuration
# See documentation for all available options

[server]
host = "0.0.0.0"
port = 8000
debug = false
log_level = "info"

[database]
url = "sqlite:///./tinybase.db"

[auth]
token_ttl_hours = 24

[functions]
path = "./functions"
file = "./functions.py"

[scheduler]
enabled = true
interval_seconds = 5

[cors]
allow_origins = ["*"]

[admin]
static_dir = "builtin"

# Environment-specific settings for deployment
# [environments.production]
# url = "https://tinybase.example.com"
# api_token = "your-admin-token"
'''


def create_example_function() -> str:
    """Generate example functions.py content."""
    return '''"""
TinyBase Functions

Define your server-side functions here. Functions are registered using
the @register decorator and automatically exposed as HTTP endpoints.
"""

from pydantic import BaseModel
from tinybase.functions import Context, register


# =============================================================================
# Example Function: Add Numbers
# =============================================================================


class AddInput(BaseModel):
    """Input model for add_numbers function."""
    x: int
    y: int


class AddOutput(BaseModel):
    """Output model for add_numbers function."""
    sum: int


@register(
    name="add_numbers",
    description="Add two numbers together",
    auth="public",  # Available without authentication
    input_model=AddInput,
    output_model=AddOutput,
    tags=["math", "example"],
)
def add_numbers(ctx: Context, payload: AddInput) -> AddOutput:
    """
    Add two numbers and return the sum.
    
    This is an example function showing how to:
    - Define input/output models with Pydantic
    - Use the @register decorator
    - Access the Context object
    """
    return AddOutput(sum=payload.x + payload.y)


# =============================================================================
# Example Function: Hello World
# =============================================================================


class HelloInput(BaseModel):
    """Input model for hello function."""
    name: str = "World"


class HelloOutput(BaseModel):
    """Output model for hello function."""
    message: str
    user_id: str | None = None


@register(
    name="hello",
    description="Say hello to someone",
    auth="auth",  # Requires authentication
    input_model=HelloInput,
    output_model=HelloOutput,
    tags=["example"],
)
def hello(ctx: Context, payload: HelloInput) -> HelloOutput:
    """
    Return a greeting message.
    
    Demonstrates accessing user information from the context.
    """
    return HelloOutput(
        message=f"Hello, {payload.name}!",
        user_id=str(ctx.user_id) if ctx.user_id else None,
    )
'''


def create_function_boilerplate(name: str, description: str) -> str:
    """Generate boilerplate code for a new function."""
    camel_name = snake_to_camel(name)
    
    return f'''

# =============================================================================
# Function: {name}
# =============================================================================


class {camel_name}Input(BaseModel):
    """Input model for {name} function."""
    # TODO: Define input fields
    pass


class {camel_name}Output(BaseModel):
    """Output model for {name} function."""
    # TODO: Define output fields
    pass


@register(
    name="{name}",
    description="{description}",
    auth="auth",
    input_model={camel_name}Input,
    output_model={camel_name}Output,
    tags=[],
)
def {name}(ctx: Context, payload: {camel_name}Input) -> {camel_name}Output:
    """
    {description}
    
    TODO: Implement function logic
    """
    return {camel_name}Output()
'''


# =============================================================================
# Commands
# =============================================================================


@app.command()
def version() -> None:
    """Show TinyBase version."""
    typer.echo(f"TinyBase v{__version__}")


@app.command()
def init(
    directory: Annotated[
        Path,
        typer.Argument(help="Directory to initialize (default: current directory)")
    ] = Path("."),
    admin_email: Annotated[
        Optional[str],
        typer.Option("--admin-email", "-e", help="Admin user email")
    ] = None,
    admin_password: Annotated[
        Optional[str],
        typer.Option("--admin-password", "-p", help="Admin user password")
    ] = None,
) -> None:
    """
    Initialize a new TinyBase instance.
    
    Creates configuration files, initializes the database, and optionally
    creates an admin user.
    """
    import os
    
    # Ensure directory exists
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    os.chdir(directory)
    
    typer.echo(f"Initializing TinyBase in {directory}")
    
    # Create tinybase.toml if missing
    toml_path = directory / "tinybase.toml"
    if not toml_path.exists():
        toml_path.write_text(create_default_toml())
        typer.echo("  Created tinybase.toml")
    else:
        typer.echo("  tinybase.toml already exists")
    
    # Create functions.py if missing
    functions_path = directory / "functions.py"
    if not functions_path.exists():
        functions_path.write_text(create_example_function())
        typer.echo("  Created functions.py with example functions")
    else:
        typer.echo("  functions.py already exists")
    
    # Create functions directory if missing
    functions_dir = directory / "functions"
    if not functions_dir.exists():
        functions_dir.mkdir()
        typer.echo("  Created functions/ directory")
    
    # Initialize database
    typer.echo("  Initializing database...")
    from tinybase.db.core import create_db_and_tables
    create_db_and_tables()
    typer.echo("  Database initialized")
    
    # Create admin user if credentials provided
    admin_email = admin_email or os.environ.get("TINYBASE_ADMIN_EMAIL")
    admin_password = admin_password or os.environ.get("TINYBASE_ADMIN_PASSWORD")
    
    if admin_email and admin_password:
        from sqlmodel import Session, select
        from tinybase.auth import hash_password
        from tinybase.db.core import get_engine
        from tinybase.db.models import User
        
        engine = get_engine()
        with Session(engine) as session:
            # Check if admin already exists
            existing = session.exec(
                select(User).where(User.email == admin_email)
            ).first()
            
            if existing:
                # Update password and ensure admin flag is set
                existing.password_hash = hash_password(admin_password)
                existing.is_admin = True
                session.add(existing)
                session.commit()
                typer.echo(f"  Updated admin user: {admin_email}")
            else:
                user = User(
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    is_admin=True,
                )
                session.add(user)
                session.commit()
                typer.echo(f"  Created admin user: {admin_email}")
    else:
        typer.echo("  Tip: Run 'tinybase admin add <email> <password>' to create an admin user")
    
    typer.echo("")
    typer.echo("TinyBase initialized successfully!")
    typer.echo("Run 'tinybase serve' to start the server.")


@app.command()
def serve(
    host: Annotated[
        Optional[str],
        typer.Option("--host", "-h", help="Host to bind to")
    ] = None,
    port: Annotated[
        Optional[int],
        typer.Option("--port", "-p", help="Port to bind to")
    ] = None,
    reload: Annotated[
        bool,
        typer.Option("--reload", "-r", help="Enable auto-reload for development")
    ] = False,
) -> None:
    """
    Start the TinyBase server.
    
    Runs the FastAPI application with Uvicorn.
    """
    import uvicorn
    
    from tinybase.config import settings
    
    config = settings()
    
    # Use CLI options or fall back to config
    bind_host = host or config.server_host
    bind_port = port or config.server_port
    
    typer.echo(f"Starting TinyBase server on {bind_host}:{bind_port}")
    typer.echo(f"  API docs: http://{bind_host}:{bind_port}/docs")
    typer.echo(f"  Admin UI: http://{bind_host}:{bind_port}/admin")
    typer.echo("")
    
    uvicorn.run(
        "tinybase.api.app:create_app",
        host=bind_host,
        port=bind_port,
        reload=reload,
        factory=True,
        log_level=config.log_level,
    )


@functions_app.command("new")
def functions_new(
    name: Annotated[
        str,
        typer.Argument(help="Function name (snake_case)")
    ],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Function description")
    ] = "TODO: Add description",
    file: Annotated[
        Path,
        typer.Option("--file", "-f", help="Functions file to add to")
    ] = Path("./functions.py"),
) -> None:
    """
    Create a new function with boilerplate code.
    
    Appends a new function template to the specified functions file.
    """
    # Validate function name
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        typer.echo(
            "Error: Function name must be lowercase with underscores (snake_case)",
            err=True
        )
        raise typer.Exit(1)
    
    # Check if file exists
    if not file.exists():
        typer.echo(f"Error: Functions file not found: {file}", err=True)
        typer.echo("Run 'tinybase init' first or specify a different file with --file")
        raise typer.Exit(1)
    
    # Check if function already exists
    content = file.read_text()
    if f'name="{name}"' in content:
        typer.echo(f"Error: Function '{name}' already exists in {file}", err=True)
        raise typer.Exit(1)
    
    # Append boilerplate
    boilerplate = create_function_boilerplate(name, description)
    
    with open(file, "a") as f:
        f.write(boilerplate)
    
    typer.echo(f"Created function '{name}' in {file}")
    typer.echo(f"  Edit the {snake_to_camel(name)}Input and {snake_to_camel(name)}Output classes to define your schema")


@functions_app.command("deploy")
def functions_deploy(
    env: Annotated[
        str,
        typer.Option("--env", "-e", help="Environment name from tinybase.toml")
    ] = "production",
) -> None:
    """
    Deploy functions to a remote TinyBase server.
    
    Reads environment configuration from tinybase.toml and uploads
    the function code to the specified server.
    """
    # This is a placeholder for the deploy functionality
    # In a full implementation, this would:
    # 1. Read environment config from tinybase.toml
    # 2. Package the function files
    # 3. Upload to the remote server
    
    typer.echo(f"Deploying functions to environment: {env}")
    typer.echo("")
    typer.echo("Note: Remote deployment is not yet implemented.")
    typer.echo("For now, deploy your functions manually by copying them to the server.")
    raise typer.Exit(1)


# =============================================================================
# Database Commands
# =============================================================================


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


# =============================================================================
# Admin Commands
# =============================================================================


@admin_app.command("add")
def admin_add(
    email: Annotated[
        str,
        typer.Argument(help="Admin user email address")
    ],
    password: Annotated[
        str,
        typer.Argument(help="Admin user password")
    ],
) -> None:
    """
    Add or update an admin user.
    
    Creates a new admin user with the given email and password.
    If the user already exists, updates their password and grants admin privileges.
    """
    from sqlmodel import Session, select
    from tinybase.auth import hash_password
    from tinybase.db.core import get_engine, create_db_and_tables
    from tinybase.db.models import User
    
    # Ensure database exists
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        # Check if user already exists
        existing = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if existing:
            existing.password_hash = hash_password(password)
            existing.is_admin = True
            session.add(existing)
            session.commit()
            typer.echo(f"Updated admin user: {email}")
        else:
            user = User(
                email=email,
                password_hash=hash_password(password),
                is_admin=True,
            )
            session.add(user)
            session.commit()
            typer.echo(f"Created admin user: {email}")


# =============================================================================
# Extension Commands
# =============================================================================


@extensions_app.command("install")
def extensions_install(
    url: Annotated[
        str,
        typer.Argument(help="GitHub repository URL (e.g., https://github.com/user/repo)")
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """
    Install an extension from a GitHub repository.
    
    Extensions can execute arbitrary Python code. Only install extensions
    from trusted sources.
    """
    from sqlmodel import Session
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.extensions import install_extension, InstallError
    
    # Security warning
    if not yes:
        typer.echo("")
        typer.echo("⚠️  WARNING: Extensions can execute arbitrary Python code.")
        typer.echo("   Only install extensions from sources you trust.")
        typer.echo("")
        confirm = typer.confirm(f"Install extension from {url}?")
        if not confirm:
            typer.echo("Installation cancelled.")
            raise typer.Exit(0)
    
    # Ensure database exists
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        try:
            typer.echo(f"Installing extension from: {url}")
            extension = install_extension(session, url)
            typer.echo("")
            typer.echo(f"✓ Successfully installed: {extension.name} v{extension.version}")
            if extension.description:
                typer.echo(f"  {extension.description}")
            typer.echo("")
            typer.echo("Note: Restart the server to load the extension.")
        except InstallError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)


@extensions_app.command("uninstall")
def extensions_uninstall(
    name: Annotated[
        str,
        typer.Argument(help="Extension name to uninstall")
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """
    Uninstall an extension.
    
    Removes the extension files and database record.
    """
    from sqlmodel import Session
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.extensions import uninstall_extension
    
    if not yes:
        confirm = typer.confirm(f"Uninstall extension '{name}'?")
        if not confirm:
            typer.echo("Uninstallation cancelled.")
            raise typer.Exit(0)
    
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        if uninstall_extension(session, name):
            typer.echo(f"✓ Uninstalled extension: {name}")
            typer.echo("")
            typer.echo("Note: Restart the server to fully unload the extension.")
        else:
            typer.echo(f"Error: Extension '{name}' not found.", err=True)
            raise typer.Exit(1)


@extensions_app.command("list")
def extensions_list() -> None:
    """
    List installed extensions.
    
    Shows all extensions with their status, version, and description.
    """
    from sqlmodel import Session, select
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.db.models import Extension
    
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        extensions = session.exec(select(Extension)).all()
        
        if not extensions:
            typer.echo("No extensions installed.")
            typer.echo("")
            typer.echo("Install an extension with:")
            typer.echo("  tinybase extensions install <github-url>")
            return
        
        typer.echo("")
        typer.echo("Installed Extensions:")
        typer.echo("-" * 60)
        
        for ext in extensions:
            status = "✓ enabled" if ext.is_enabled else "○ disabled"
            typer.echo(f"\n  {ext.name} v{ext.version}  [{status}]")
            if ext.description:
                typer.echo(f"    {ext.description}")
            if ext.author:
                typer.echo(f"    Author: {ext.author}")
            typer.echo(f"    Source: {ext.repo_url}")
        
        typer.echo("")


@extensions_app.command("enable")
def extensions_enable(
    name: Annotated[
        str,
        typer.Argument(help="Extension name to enable")
    ],
) -> None:
    """
    Enable an extension.
    
    The extension will be loaded on the next server restart.
    """
    from sqlmodel import Session, select
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.db.models import Extension
    from tinybase.utils import utcnow
    
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        extension = session.exec(
            select(Extension).where(Extension.name == name)
        ).first()
        
        if not extension:
            typer.echo(f"Error: Extension '{name}' not found.", err=True)
            raise typer.Exit(1)
        
        if extension.is_enabled:
            typer.echo(f"Extension '{name}' is already enabled.")
            return
        
        extension.is_enabled = True
        extension.updated_at = utcnow()
        session.add(extension)
        session.commit()
        
        typer.echo(f"✓ Enabled extension: {name}")
        typer.echo("")
        typer.echo("Note: Restart the server to load the extension.")


@extensions_app.command("disable")
def extensions_disable(
    name: Annotated[
        str,
        typer.Argument(help="Extension name to disable")
    ],
) -> None:
    """
    Disable an extension.
    
    The extension will not be loaded on the next server restart.
    """
    from sqlmodel import Session, select
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.db.models import Extension
    from tinybase.utils import utcnow
    
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        extension = session.exec(
            select(Extension).where(Extension.name == name)
        ).first()
        
        if not extension:
            typer.echo(f"Error: Extension '{name}' not found.", err=True)
            raise typer.Exit(1)
        
        if not extension.is_enabled:
            typer.echo(f"Extension '{name}' is already disabled.")
            return
        
        extension.is_enabled = False
        extension.updated_at = utcnow()
        session.add(extension)
        session.commit()
        
        typer.echo(f"✓ Disabled extension: {name}")
        typer.echo("")
        typer.echo("Note: Restart the server to fully unload the extension.")


@extensions_app.command("check-updates")
def extensions_check_updates(
    name: Annotated[
        Optional[str],
        typer.Argument(help="Extension name (omit to check all)")
    ] = None,
) -> None:
    """
    Check for extension updates.
    
    Compares installed versions with the latest versions from GitHub.
    """
    from sqlmodel import Session, select
    from tinybase.db.core import create_db_and_tables, get_engine
    from tinybase.db.models import Extension
    from tinybase.extensions import check_for_updates
    
    create_db_and_tables()
    
    engine = get_engine()
    with Session(engine) as session:
        if name:
            extensions = [session.exec(
                select(Extension).where(Extension.name == name)
            ).first()]
            if not extensions[0]:
                typer.echo(f"Error: Extension '{name}' not found.", err=True)
                raise typer.Exit(1)
        else:
            extensions = list(session.exec(select(Extension)).all())
        
        if not extensions:
            typer.echo("No extensions installed.")
            return
        
        typer.echo("Checking for updates...")
        typer.echo("")
        
        updates_available = False
        for ext in extensions:
            if not ext:
                continue
            result = check_for_updates(session, ext.name)
            if result:
                current, latest = result
                typer.echo(f"  {ext.name}: {current} → {latest} (update available)")
                updates_available = True
            else:
                typer.echo(f"  {ext.name}: {ext.version} (up to date)")
        
        if updates_available:
            typer.echo("")
            typer.echo("To update an extension, uninstall and reinstall it:")
            typer.echo("  tinybase extensions uninstall <name>")
            typer.echo("  tinybase extensions install <github-url>")


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()

