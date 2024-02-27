import argparse
import os
import sys

from . import trigger


def main() -> int:
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]))
    parser.add_argument("-t", "--token", help="Cirrus-CI TOKEN", required=True)
    parser.add_argument("-r", "--repository", help="GitHub repository", required=True)
    parser.add_argument(
        "-b", "--branch", help="The branch of the repository", required=True
    )
    parser.add_argument("-c", "--config", help="The configuration YAML", default="")
    parser.add_argument("-T", "--timeout", help="Timeout (in minutes)", type=int)
    parser.add_argument(
        "-i", "--interval", help="Sleep interval (in seconds)", type=int
    )
    try:
        args = parser.parse_args()
    except Exception:
        parser.print_help()
        return 128

    trigger.trigger(args)
    return 0
