import os

import pytest


@pytest.fixture
def resources_dir():
    return './tests/resources/'


@pytest.fixture
def empty_dir(resources_dir):
    return os.path.join(resources_dir, 'empty_dir')


@pytest.fixture
def naffile_coref(resources_dir):
    return os.path.join(resources_dir, 'coref.naf')


@pytest.fixture
def naffile_no_coref(resources_dir):
    return os.path.join(resources_dir, 'no_coref.naf')


@pytest.fixture
def naffile_not_consec_coref(resources_dir):
    return os.path.join(resources_dir, 'not_consec_coref.naf')


@pytest.fixture
def nafobj(naffile_coref):
    from KafNafParserPy import KafNafParser
    return KafNafParser(naffile_coref)


@pytest.fixture
def fill_spans_config(resources_dir):
    return os.path.join(resources_dir, 'fill_spans_config.yml')
