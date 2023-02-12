import pytest
import pytest_mock
import pytest_raises
import os

from autobackup import appinit


def test_init_app_AppInitComplete(testdir):
    # Arrange
    testdata_root = testdir(__name__)

    # Act
    appinit.init_app(
        {
            "common": {
                "tmp_dirpath": f"{testdata_root}/tmp",
                "var_dirpath": f"{testdata_root}/var",
                "log_dirpath": f"{testdata_root}/var/log",
            }
        }
    )

    # Assert
    assert os.path.exists(f"{testdata_root}/tmp")
    assert os.path.exists(f"{testdata_root}/var")
    assert os.path.exists(f"{testdata_root}/var/log")


def test_init_app_IfAlreadyExistDirThenAppInitComplete(testdir):
    # Arrange
    testdata_root = testdir(__name__)
    os.mkdir(f"{testdata_root}/tmp")
    os.mkdir(f"{testdata_root}/var")

    # Act
    appinit.init_app(
        {
            "common": {
                "tmp_dirpath": f"{testdata_root}/tmp",
                "var_dirpath": f"{testdata_root}/var",
                "log_dirpath": f"{testdata_root}/var/log",
            }
        }
    )

    # Assert
    assert os.path.exists(f"{testdata_root}/tmp")
    assert os.path.exists(f"{testdata_root}/var")
    assert os.path.exists(f"{testdata_root}/var/log")
