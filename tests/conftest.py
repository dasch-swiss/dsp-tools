import os

import pytest

import knora.create_ontology


@pytest.fixture
def create_test_ontology_fixture():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    knora.create_ontology.main(['./test-onto.json'])
