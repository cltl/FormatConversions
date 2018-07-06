import os
import sys
import logging
import subprocess

from naf2conll.main import Main

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


def test_fill_spans(caplog, naffile_not_consec_coref, fill_spans_config):
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
                naffile_not_consec_coref,
                '-c',
                fill_spans_config
            ],
            check=True
        )
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def test_problem_only(caplog, naffile_not_consec_coref, problem_only_config):
    caplog.set_level(logging.DEBUG)
    output_file = 'output.conll'
    try:
        Main.main([
            output_file,
            naffile_not_consec_coref,
            '-c',
            problem_only_config
        ]),
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def test_default_config(caplog, naffile_coref, default_config):
    caplog.set_level(logging.DEBUG)
    output_file = 'output.conll'
    try:
        Main.main([
            output_file,
            naffile_coref,
            '-c',
            default_config
        ]),
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def test_not_fill_spans(caplog, naffile_not_consec_coref):
    caplog.set_level(logging.DEBUG)
    logger.debug(os.path.realpath(os.curdir))
    output_file = 'output.conll'
    try:
        res = subprocess.run(
            [
                sys.executable,
                "-m",
                "naf2conll",
                output_file,
                naffile_not_consec_coref,
            ]
        )
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
    assert res.returncode != 0
