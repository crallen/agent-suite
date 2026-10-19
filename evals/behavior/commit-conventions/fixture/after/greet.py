"""Print a greeting for the name given on the command line.

Pass --shout to print it in capitals.
"""

import sys


def greeting(name: str, shout: bool = False) -> str:
    text = f"Hello, {name}!"
    return text.upper() if shout else text


if __name__ == "__main__":
    args = sys.argv[1:]
    shout = "--shout" in args
    names = [arg for arg in args if arg != "--shout"]
    print(greeting(names[0] if names else "world", shout=shout))
