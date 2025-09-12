"""Command Line Interface for serial communication."""

import os
import re
from importlib.metadata import version

import rich_click as click

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(version("serial-cli"))
def main():
    """Serial CLI Tool"""


@click.option(
    "-b",
    "--baudrate",
    default=9600,
    type=click.INT,
    help="Set the baudrate for serial communication",
)
@click.option(
    "-p",
    "--port",
    default=("/dev/ttyUSB0" if os.name != "nt" else "COM3"),
    type=click.STRING,
    help="Set the serial port to use",
)
@click.option(
    "--timeout",
    default=5,
    type=click.INT,
    help="Set the timeout for serial communication",
)
@main.command()
def shell(port, baudrate, timeout):
    """Start an interactive shell session."""
    import subprocess

    from rich.console import Console
    from rich.text import Text
    from serial import Serial

    with Serial(port, baudrate, timeout=timeout) as serial:
        click.echo(f"Connected to {port} at {baudrate} baud.")

        console = Console()

        while True:
            prompt_text = Text(f"{port}> ", style="bold green")
            stdin = console.input(prompt_text)

            match stdin.lower():
                case "exit":
                    break
                case "clear":
                    console.clear()
                    continue

            try:
                # Check if this is a command for the terminal or text to send over serial
                if stdin.strip().startswith("!"):
                    # Terminal command (starts with !)
                    command = stdin[1:].strip()

                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    console.print(result.stdout, style="white")
                    if result.stderr:
                        console.print(result.stderr, style="red")
                    continue

                # Send expanded text over serial
                serial.write((stdin + "\n").encode())

                received = serial.read_until(b"\n\n")
                # Highlight hex values in the response
                highlighted_line = re.sub(
                    r"(0x[0-9A-Fa-f]{2})",
                    r"[bold yellow]\1[/bold yellow]",
                    received.decode().strip(),
                )
                console.print(highlighted_line, style="white")

                console.print(
                    f"Sent: {len(stdin.encode())}b, Received: {len(received)}b",
                    style="cyan",
                )

            except subprocess.CalledProcessError as e:
                console.print(f"Error: {e.stderr}", style="red")
            except FileNotFoundError:
                console.print(
                    f"[bold red]Command not found:[/bold red] {stdin}"
                )
            except Exception as e:
                console.print(
                    f"[bold red]An unexpected error occurred:[/bold red] {e}"
                )
