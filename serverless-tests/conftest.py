import pytest


def pytest_addoption(parser):
    parser.addoption("--remote", action="store_true")
    parser.addoption("--stage", action="store")


@pytest.fixture
def make_sls_cmd(pytestconfig):
    def _make(function, event_path):
        cmd = ["pipenv", "run", "serverless", "invoke"]
        if not pytestconfig.getoption("remote"):
            cmd.append("local")
        if pytestconfig.getoption("stage"):
            cmd.append("--stage")
            cmd.append(pytestconfig.getoption("stage"))
        cmd.append("-f")
        cmd.append(function)
        cmd.append("-p")
        cmd.append(event_path)

        return cmd

    return _make
