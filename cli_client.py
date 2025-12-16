import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
CLI_PATH = Path(__file__).parent / "CLI.py"


def run_cli(command: str, allow_fail: bool = False):
    full_cmd = f'"{PYTHON}" "{CLI_PATH}" {command}'
    print("\n>", full_cmd)

    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stdout.strip())
        print(result.stderr.strip())

        if not allow_fail:
            raise RuntimeError("CLI command failed")

    else:
        print(result.stdout.strip())

    return result


def create_function():
    run_cli(
        'create '
        '--name cubic '
        '--code "def f(x, a=1, b=0, c=0, d=0): return a*x*x*x + b*x*x + c*x + d" '
        '--description "Cubic function"',
        allow_fail=True
    )


def get_function_info():
    run_cli('get --name cubic')


def compute_function():
    run_cli(
        'compute '
        '--name cubic '
        '--x "0,1,2,3" '
        '--params a=1 b=0 c=0 d=1'
    )


def list_functions():
    run_cli('list')


if __name__ == "__main__":
    list_functions()
    create_function()
    get_function_info()
    compute_function()
