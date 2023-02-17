import pytest
import pytest_mock
import pytest_raises
import os

from autobackup import appinit


class Test_init_app:
    @staticmethod
    def test_AppInitComplete(testdir):
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

    @staticmethod
    def test_IfAlreadyExistDirThenAppInitComplete(testdir):
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
