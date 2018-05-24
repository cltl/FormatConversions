from os import path
from argparse import ArgumentTypeError


class ValidationError(ValueError):
    pass


def file_exists(filename):
    if not path.exists(filename):
        raise ArgumentTypeError(f"No such file: {filename}")
    return filename
