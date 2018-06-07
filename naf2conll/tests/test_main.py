import os
import sys
import logging
import subprocess

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def test_empty_dir(caplog, empty_dir):
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
                empty_dir
            ],
            check=True
        )
    finally:
        if os.path.exists(output_dir):
            os.rmdir(output_dir)


def test_no_coref_file(caplog, naffile_no_coref):
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
                naffile_no_coref
            ],
            check=True
        )
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def test_coref_file(caplog, naffile_coref):
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
                naffile_coref
            ],
            check=True
        )
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
