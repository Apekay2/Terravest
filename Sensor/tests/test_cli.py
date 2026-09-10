from importlib.metadata import version

from adr_sensor.cli import get_version


def test_cli_version_matches_package_metadata():
    assert get_version() == version("adr-sensor")
