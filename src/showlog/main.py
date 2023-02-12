"""Module of main"""
import argparse
import os
import time


def main(args: list[str]) -> int:
    """
    Main method.

    Args:
        args (list[str]): Commandline arguments

    Returns:
        int: Exit code of command
    """
    exit_code = 0

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path of the file to open.")
    parser.add_argument(
        "--interval",
        help="The interval to be checked in seconds.",
        type=float,
        default=15.0,
    )
    parser.add_argument(
        "--encoding",
        help="The interval to be checked in seconds.",
        default=None,
    )
    parsed_args = parser.parse_args(args[1::])
    with open(parsed_args.file, encoding=parsed_args.encoding) as file:
        while True:
            line = file.readline().rstrip(os.linesep)
            if not line:
                time.sleep(parsed_args.interval)
                continue
            print(line)
    return exit_code
