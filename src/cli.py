"""Command Line Interface for AI Automation Boilerplate."""

import asyncio
import click
from alembic.config import Config
from alembic import command as alembic_command


@click.group()
def main():
    """AI Automation Boilerplate CLI."""
    pass


@main.command()
def version():
    """Show the version."""
    click.echo("AI Automation Boilerplate v0.1.0")


@main.command()
def serve():
    """Start the AI automation server."""
    click.echo("Starting AI automation server...")
    # Import here to avoid issues if dependencies aren't installed
    try:
        from .api import app
        from .config import get_settings
        import uvicorn
        
        settings = get_settings()
        uvicorn.run(
            app,
            host=settings.api.host,
            port=settings.api.port,
            reload=settings.api.reload,
        )
    except ImportError as e:
        click.echo(f"Error starting server: {e}")
        click.echo("Make sure all dependencies are installed.")


@main.command()
@click.option("--input", "-i", help="Input file or data")
@click.option("--output", "-o", help="Output file")
def process(input, output):
    """Process data using AI automation."""
    click.echo(f"Processing {input} -> {output}")
    # Placeholder for data processing functionality


@main.group()
def db():
    """Database management commands."""
    pass


@db.command()
def init():
    """Initialize the database."""
    click.echo("Initializing database...")
    alembic_cfg = Config("alembic.ini")
    alembic_command.upgrade(alembic_cfg, "head")
    click.echo("✓ Database initialized successfully")


@db.command()
@click.option("--message", "-m", required=True, help="Migration message")
def migrate(message):
    """Create a new migration."""
    click.echo(f"Creating migration: {message}")
    alembic_cfg = Config("alembic.ini")
    alembic_command.revision(alembic_cfg, message=message, autogenerate=True)
    click.echo("✓ Migration created successfully")


@db.command()
def upgrade():
    """Upgrade database to latest version."""
    click.echo("Upgrading database...")
    alembic_cfg = Config("alembic.ini")
    alembic_command.upgrade(alembic_cfg, "head")
    click.echo("✓ Database upgraded successfully")


@db.command()
def downgrade():
    """Downgrade database by one version."""
    click.echo("Downgrading database...")
    alembic_cfg = Config("alembic.ini")
    alembic_command.downgrade(alembic_cfg, "-1")
    click.echo("✓ Database downgraded successfully")


@db.command()
def seed():
    """Seed the database with demo data."""
    click.echo("Seeding database...")
    
    async def _seed():
        from .database import AsyncSessionLocal
        from .database.models import Agent, Workflow
        from datetime import datetime
        
        async with AsyncSessionLocal() as session:
            # Create demo agent
            demo_agent = Agent(
                name="demo_email_processor",
                description="Demo agent for processing emails",
                agent_type="task",
                config={
                    "name": "demo_email_processor",
                    "description": "Demo agent for processing emails",
                    "task_type": "email_processing",
                    "required_tools": ["email_reader", "categorizer"],
                    "max_retries": 3,
                    "timeout": 300
                },
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(demo_agent)
            
            # Create demo workflow
            demo_workflow = Workflow(
                name="demo_data_processing",
                description="Demo workflow for data processing",
                steps=[
                    {
                        "id": "step1",
                        "name": "Load Data",
                        "agent_type": "task",
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "name": "Process Data",
                        "agent_type": "task",
                        "depends_on": ["step1"]
                    },
                    {
                        "id": "step3",
                        "name": "Save Results",
                        "agent_type": "task",
                        "depends_on": ["step2"]
                    }
                ],
                config={
                    "name": "demo_data_processing",
                    "timeout": 600,
                    "parallel_execution": False
                },
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(demo_workflow)
            
            await session.commit()
    
    asyncio.run(_seed())
    click.echo("✓ Database seeded successfully")


@db.command()
def reset():
    """Reset the database (drop and recreate)."""
    if click.confirm("This will delete all data. Are you sure?"):
        click.echo("Resetting database...")
        alembic_cfg = Config("alembic.ini")
        alembic_command.downgrade(alembic_cfg, "base")
        alembic_command.upgrade(alembic_cfg, "head")
        click.echo("✓ Database reset successfully")


if __name__ == "__main__":
    main()
