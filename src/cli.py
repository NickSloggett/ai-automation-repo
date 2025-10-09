"""Command Line Interface for AI Automation Boilerplate."""

import click


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
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)
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


if __name__ == "__main__":
    main()
