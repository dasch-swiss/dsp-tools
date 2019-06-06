import pytest

# we reuse a bit of pytest's own testing machinery, this should eventually come
# from a separatedly installable pytest-cli plugin.
pytest_plugins = ["pytester"]

@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ["knora-create-ontology"] + list(args)
        return testdir._run(*args)
    return do_run


def test_create_test_onto(tmpdir, run):
    input = tmpdir.join("test-onto.json")
    result = run(input)
    assert result.ret == 0
