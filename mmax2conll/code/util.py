from os import path
from argparse import ArgumentTypeError


class ValidationError(ValueError):
    pass


def is_consecutive(positions):
    """
    Validate the words in a span are consecutive.

    Assumes:
     - the span is a list of word IDs
    """
    positions = list(positions)
    return all(
        expected == pos
        for expected, pos in zip(
            range(positions[0], positions[0] + len(positions)),
            positions
        )
    )


def file_exists(filename):
    if not path.exists(filename):
        raise ArgumentTypeError(f"No such file: {filename}")
    return filename
