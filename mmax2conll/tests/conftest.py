import os

import pytest


@pytest.fixture
def resources_dir():
    return './resources/'


@pytest.fixture
def config_dir():
    return '../config/'


@pytest.fixture
def empty_dir(resources_dir):
    return os.path.join(resources_dir, 'empty_dir')


@pytest.fixture
def corea_dir(resources_dir):
    return os.path.join(resources_dir, 'COREA')


@pytest.fixture
def sonar_dir(resources_dir):
    return os.path.join(resources_dir, 'SONAR_1_COREF')


@pytest.fixture
def corea_config(config_dir):
    return os.path.join(config_dir, 'COREA_config.yml')


@pytest.fixture
def sonar_config(config_dir):
    return os.path.join(config_dir, 'SoNaR_config.yml')


@pytest.fixture
def sonar_fill_spans_config(config_dir):
    return os.path.join(config_dir, 'SoNaR_fill_config.yml')


@pytest.fixture
def sonar_problem_only_config(config_dir):
    return os.path.join(config_dir, 'SoNaR_problem_only_config.yml')
