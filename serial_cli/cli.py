"""Command Line Interface for serial communication."""

import os

import rich_click as click

import serial_cli
from serial_cli.core import SerialCLI

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(serial_cli.__version__, "-v", "--version")
def main():
    """Serial CLI Tool"""


@main.command()
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
    type=click.Path(exists=True) if os.name != "nt" else click.STRING,
    help="Set the serial port to use",
)
@click.option(
    "--timeout",
    default=5,
    type=click.INT,
    help="Set the timeout for serial communication",
)
def shell(port: str, baudrate: int, timeout: int):
    """Start an interactive shell session."""
    with SerialCLI(port, baudrate, timeout=timeout) as serial:
        serial.shell()


@main.command()
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
    type=click.Path(exists=True) if os.name != "nt" else click.STRING,
    help="Set the serial port to use",
)
@click.option(
    "--timeout",
    default=5,
    type=click.INT,
    help="Set the timeout for serial communication",
)
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def run(files: list[str], port: str, baudrate: int, timeout: int):
    """Start an interactive shell session."""
    import fileinput

    with SerialCLI(port, baudrate, timeout=timeout) as serial:
        try:
            with fileinput.input(files=files) as file:
                for line in file:
                    serial.exec(line)
        except Exception as e:
            serial.console.print(str(e), style="bold red")
