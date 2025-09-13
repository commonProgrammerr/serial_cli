import re
import subprocess

from rich.console import Console
from rich.text import Text
from serial import Serial


class SerialCLI(Serial):
    console: Console

    def __init__(
        self,
        port=None,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=None,
        xonxoff=False,
        rtscts=False,
        write_timeout=None,
        dsrdtr=False,
        inter_byte_timeout=None,
        exclusive=None,
    ):
        super().__init__(
            port,
            baudrate,
            bytesize,
            parity,
            stopbits,
            timeout,
            xonxoff,
            rtscts,
            write_timeout,
            dsrdtr,
            inter_byte_timeout,
            exclusive,
        )
        self.console = Console()
        self.console.print(
            f"[green]Connected to {port} at {baudrate} baud.[green]"
        )

    def _sanitize_output(self, received: bytes) -> str:
        return re.sub(
            r"(0x[0-9A-Fa-f]{2})",
            r"[bold yellow]\1[/bold yellow]",
            received.decode().strip(),
        )

    def _run_subcommand(self, cmd: str, print_output=True):
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        if print_output:
            self.console.print(result.stdout, style="white")

        if result.stderr:
            self.console.print(result.stderr, style="red")

        return result

    def shell(self):
        while True:
            prompt_text = Text(f"{super().port}> ", style="bold green")
            stdin = self.console.input(prompt_text)

            match stdin.lower():
                case "exit":
                    break
                case "clear":
                    self.console.clear()
                    continue

            try:
                # Check if this is a command for the terminal or text to send over serial
                if stdin.strip().startswith("!"):
                    # Terminal command (starts with !)
                    command = stdin[1:].strip()
                    self._run_subcommand(command)
                    continue

                # Send expanded text over serial
                bytes_sent = self.send((stdin + "\n"))

                # read all until receive \n\n or timeout
                received = self.read_until(b"\n\n")

                self.console.print(
                    self._sanitize_output(received), style="white"
                )

                self.console.print(
                    f"Sent: {bytes_sent}b, Received: {len(received)}b",
                    style="cyan",
                )

            except subprocess.CalledProcessError as e:
                self.console.print(f"Error: {e.stderr}", style="red")
            except FileNotFoundError:
                self.console.print(
                    f"[bold red]Command not found:[/bold red] {stdin}"
                )
            except Exception as e:
                self.console.print(
                    f"[bold red]An unexpected error occurred:[/bold red] {e}"
                )

    def exec(self, line: str):
        match line.lower():
            case line if line.startswith("!"):
                sp = self._run_subcommand(line[1:].strip())
                if sp.returncode > 0:
                    raise RuntimeError(f"Command fail: {line}")

            case line if line.startswith("send "):
                return self.send(line.removeprefix("send "))

    def send(self, text: str):
        subcommand_pattern = re.compile(r"!\(([^)]+)\)")

        for subcommand in subcommand_pattern.findall(text):
            sp = self._run_subcommand(subcommand, print_output=False)
            if sp.returncode > 0:
                raise RuntimeError(f"Command fail: {subcommand}")

            text = re.sub(f"!\\({subcommand}\\)", sp.stdout, text, 1)

        output = text.encode()
        self.writelines(output.splitlines(True))

        return len(output)
