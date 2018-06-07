import os
import sys
import logging
import subprocess

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def test_empty_dir(caplog):
    caplog.set_level(logging.DEBUG)
    logger.debug(os.path.realpath(os.curdir))
    output_dir = 'output_dir'
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "naf2conll",
                output_dir,
                "-d",
                "./tests/resources/empty_dir"
            ],
            check=True
        )
    finally:
        if os.path.exists(output_dir):
            os.rmdir(output_dir)


def test_no_coref_file(caplog):
    caplog.set_level(logging.DEBUG)
    logger.debug(os.path.realpath(os.curdir))
    output_file = 'output.conll'
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "naf2conll",
                output_file,
                "./tests/resources/no_coref.naf"
            ],
            check=True
        )
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
