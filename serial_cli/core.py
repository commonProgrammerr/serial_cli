import os
import re
import subprocess

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.text import Text
from serial import Serial


class SerialCLI(Serial):
    console: Console
    history: FileHistory

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

    def iterative_shell(self):
        history_file = os.path.expanduser("~/.serial_cli_history")
        self.console.print(
            Text.assemble(
                ("Entering interactive mode. Type ", "white"),
                ("exit", "bold red"),
                (" to quit.\n", "white"),
            )
        )
        self.history = FileHistory(history_file)
        styled_prompt = FormattedText([("fg:#00ff00", f"{self.port}> ")])
        while True:
            try:
                line = prompt(
                    styled_prompt,
                    history=self.history,
                    auto_suggest=AutoSuggestFromHistory(),
                )
                if line.strip():
                    self.exec(line, iterative=True)
            except (EOFError, KeyboardInterrupt):
                return
            except ValueError as e:
                self.console.print(str(e), style="bold red")
            except FileNotFoundError:
                self.console.print(
                    f"[bold red]Command not found:[/bold red] {line[1:].strip().split(' ')[0]}",
                )

                self.console.print(
                )
            except FileNotFoundError:
                self.console.print(
                )

    def exec(self, line: str, verbose=False):
        line = re.sub(r"#.*$", "", line)  # remove comments
        if line.strip().startswith("!"):
            sp = self._run_subcommand(line[1:].strip())
            if sp.returncode > 0:
                raise RuntimeError(f"Command fail: {line}")
            return

        match line.strip().split(" ", 1):
            case ["clear", *_]:
                self.console.clear()
            case ["exit", *_]:
                raise KeyboardInterrupt()
            case ["read", total, *_] if re.match(r"^\d+$", total):
                self.console.print(
                    self._sanitize_output(self.read(int(total))),
                    style="white",
                )
            case ["read", end, *_] if re.match(r"^\w+$", end):
                self.console.print(
                    self._sanitize_output(self.read_until(end.encode())),
                    style="white",
                )
            case ["send", data] | ["write", data]:
                if should_wait_response := "--wait" in data.split(" "):
                    data = data.replace("--wait", "", 1).strip()

                # send the rest of the line
                bytes_sent = self.send(data)

                if should_wait_response:
                    # read all until receive \n\n or timeout
                    bytes_received = self.receive(b"\n\n")

                    self.console.print(
                        self._sanitize_output(bytes_received), style="white"
                    )

                if verbose:
                    self.console.print(
                        f"Sent: {bytes_sent}b, Received: {len(bytes_received)}b",
                        style="cyan",
                    )
            case _:
                raise ValueError(f"Unknown command: {line}")

    def send(self, text: str):
        subcommand_pattern = re.compile(r"!\(([^)]+)\)")

        for subcommand in subcommand_pattern.findall(text):
            sp = self._run_subcommand(subcommand, print_output=False)
            if sp.returncode > 0:
                raise RuntimeError(f"Command fail: {subcommand}")

            text = subcommand_pattern.sub(sp.stdout, text, 1)

        output = text.encode()
        self.writelines(output.splitlines(True))

        return len(output)

    def receive(self, arg: Union[int, bytes]) -> bytes:

        if isinstance(arg, int):
            result = self.read(arg)
        elif isinstance(arg, bytes):
            result = self.read_until(arg)
        else:
            raise ValueError(
                "Argument must be int (size) or bytes (end sequence)"
            )

        return result
