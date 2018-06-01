import os
from argparse import ArgumentTypeError


class ValidationError(ValueError):
    pass


def file_exists(filename):
    """
    Ensure a path exists

    Raise ArgumentTypeError if it doesn't.
    """
    if not os.path.exists(filename):
        raise ArgumentTypeError(f"No such file: {filename}")
    return filename


def directory_exists(dirname):
    """
    Ensure a path exists and that it has a trailing slash

    Raise ArgumentTypeError if it doesn't.
    """
    return os.path.join(file_exists(dirname), '')
