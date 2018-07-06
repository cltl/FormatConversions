import os
import shutil
import logging

from mmax2conll.main import Main

logger = logging.getLogger(None if __name__ == '__main__' else __name__)


def test_corea_empty_dir(caplog, empty_dir, corea_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            corea_config,
            output_dir,
            "-d",
            empty_dir
        ])
        assert not os.path.exists(output_dir)
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO


def test_sonar_empty_dir(caplog, empty_dir, sonar_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            sonar_config,
            output_dir,
            "-d",
            empty_dir
        ])
        assert not os.path.exists(output_dir)
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO


def test_sonar_fill_spans(caplog, sonar_dir, sonar_fill_spans_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            sonar_fill_spans_config,
            output_dir,
            "-d",
            sonar_dir
        ])
        assert len(os.listdir(output_dir)) == 1
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO


def test_sonar_problem_only(caplog, sonar_dir, sonar_problem_only_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            sonar_problem_only_config,
            output_dir,
            "-d",
            sonar_dir
        ])
        assert len(os.listdir(output_dir)) == 1
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO


def test_corea(caplog, corea_dir, corea_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            corea_config,
            output_dir,
            "-d",
            corea_dir
        ])
        assert len(os.listdir(output_dir)) == 1
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO


def test_sonar(caplog, sonar_dir, sonar_config):
    caplog.set_level(logging.DEBUG)
    output_dir = 'output_dir'
    try:
        Main.main([
            sonar_config,
            output_dir,
            "-d",
            sonar_dir
        ])
        assert len(os.listdir(output_dir)) == 1
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    for record in caplog.records:
        assert record.levelno <= logging.INFO
