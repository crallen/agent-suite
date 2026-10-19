"""Print a greeting for the name given on the command line."""

import sys


def greeting(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greeting(sys.argv[1] if len(sys.argv) > 1 else "world"))
