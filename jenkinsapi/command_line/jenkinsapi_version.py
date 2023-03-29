"""
Invokable module used to print jenkinsapi version.
"""


from jenkinsapi import __version__ as version
import sys


def main():
    # type: () -> None
    """
    Writes the current jenkinsapi version to stdout.
    """
    sys.stdout.write(version)


if __name__ == "__main__":
    main()
