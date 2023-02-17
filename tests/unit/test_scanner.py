import pytest
import pytest_mock
import pytest_raises
from os import sep

from autobackup import scanner
from tests.testutil import testpath


class Test_AllFileScanner_get_all_files:
    @staticmethod
    def test_GetAllFilesUnderTargetDir(testdata_fresh):
        # Arrange
        target_root = testdata_fresh(__name__)

        targets = [
            testpath.src_testdir1_path(target_root, norm_path=False),
            testpath.src_testdir2_path(target_root, norm_path=False),
        ]

        scnr = scanner.AllFileScanner(targets, False)

        # Act
        actual = [str(file.relpath) for key, file in scnr.get_all_files().items()]

        # Assert
        assert set(actual) == set(
            [
                "TestFile11",
                ".old" + sep + "TestFile11_2023-01-23_0000",
                "TestFile12.ext",
                ".old" + sep + "TestFile12_2023-01-23_0000.ext",
                ".TestFile21",
                ".old" + sep + ".TestFile21_2023-01-23_0000",
                "TestFile22",
                ".old" + sep + "TestFile22_2023-01-23_0000",
            ]
        )
