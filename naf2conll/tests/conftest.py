import pytest


@pytest.fixture
def empty_dir():
    return './tests/resources/empty_dir'


@pytest.fixture
def naffile_coref():
    return './tests/resources/coref.naf'


@pytest.fixture
def naffile_no_coref():
    return './tests/resources/no_coref.naf'


@pytest.fixture
def nafobj(naffile_coref):
    from KafNafParserPy import KafNafParser
    return KafNafParser(naffile_coref)
