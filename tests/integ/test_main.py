import pytest
import pytest_mock
import pytest_raises
import os
import time
from tests.testutil import testpath, build_path

from autobackup import main


def test_main_CreateBackup(testdir, testdata, testdata_timestamp, rscan):
    # Arrange
    expected_logs = [
        "START: autobackup",
        "SCAN_DIR: ",
        "SCANNED_FILE_COUNT: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "FINISH: autobackup",
        "START: autobackup",
        "SCAN_DIR: ",
        "SCANNED_FILE_COUNT: ",
        "COPY_FILE_TO_",
        "REPLACE_INTO_DB: ",
        "FINISH: autobackup",
    ]
    test_dir = testdir(__name__)
    target_root = testdata(__name__)
    args = [
        "progname",
        "--cnf_dirpath",
        "tests/data/cnf",
    ]
    main_obj = main.Main(args)

    # Act

    actual1 = main_obj.execute()
    # rscan fixture returns Generator (yield return)
    actual2 = [item for item in rscan(target_root)]

    os.utime(
        testpath.src_testfile11_path(target_root),
        (testdata_timestamp, testdata_timestamp + 0.001),
    )

    actual3 = main_obj.execute()
    actual4 = rscan(target_root)

    with open(
        test_dir + os.sep + "var" + os.sep + "log" + os.sep + "autobackup.log", "r"
    ) as fp:
        actual5 = fp.readlines()

    # Assert
    assert actual1 == 0
    assert set(actual2) == set(
        [
            "TestFile",
            ".old" + os.sep + "TestFile_2023-01-23_0000",
            "TestDir1" + os.sep + "TestFile11",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile11_2023-01-23_0000",
            "TestDir1" + os.sep + "TestFile12.ext",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile12_2023-01-23_0000.ext",
            "TestDir2" + os.sep + ".TestFile21",
            "TestDir2" + os.sep + ".old" + os.sep + ".TestFile21_2023-01-23_0000",
            "TestDir2" + os.sep + "TestFile22",
            "TestDir2" + os.sep + ".old" + os.sep + "TestFile22_2023-01-23_0000",
        ]
    )
    assert actual3 == 0
    assert set(actual4) == set(
        [
            "TestFile",
            ".old" + os.sep + "TestFile_2023-01-23_0000",
            "TestDir1" + os.sep + "TestFile11",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile11_2023-01-23_0000",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile11_2023-01-23_0001",
            "TestDir1" + os.sep + "TestFile12.ext",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile12_2023-01-23_0000.ext",
            "TestDir2" + os.sep + ".TestFile21",
            "TestDir2" + os.sep + ".old" + os.sep + ".TestFile21_2023-01-23_0000",
            "TestDir2" + os.sep + "TestFile22",
            "TestDir2" + os.sep + ".old" + os.sep + "TestFile22_2023-01-23_0000",
        ]
    )
    assert len(actual5) == len(expected_logs)
    for line, expected in zip(actual5, expected_logs):
        assert expected in line


import pytest
import pytest_mock
import pytest_raises
import os
import time
from tests.testutil import testpath, build_path

from autobackup import main


def test_main_IfAlreadyBackedUpThenSkipBackup(
    testdir, testdata_fresh, testdata_timestamp, rscan
):
    # Arrange
    expected_logs = [
        "START: autobackup",
        "SCAN_DIR: ",
        "SCANNED_FILE_COUNT: ",
        "SKIP(Already):",
        "REPLACE_INTO_DB:",
        "SKIP(Already):",
        "REPLACE_INTO_DB:",
        "SKIP(Already):",
        "REPLACE_INTO_DB:",
        "SKIP(Already):",
        "REPLACE_INTO_DB:",
        "SKIP(Already):",
        "REPLACE_INTO_DB:",
        "FINISH: autobackup",
    ]
    test_dir = testdir(__name__)
    target_root = testdata_fresh(__name__)
    args = [
        "progname",
        "--cnf_dirpath",
        "tests/data/cnf",
    ]
    main_obj = main.Main(args)

    # Act

    actual1 = main_obj.execute()
    # rscan fixture returns Generator (yield return)
    actual2 = [item for item in rscan(target_root)]

    with open(
        test_dir + os.sep + "var" + os.sep + "log" + os.sep + "autobackup.log", "r"
    ) as fp:
        actual3 = fp.readlines()

    # Assert
    assert actual1 == 0
    assert set(actual2) == set(
        [
            "TestFile",
            ".old" + os.sep + "TestFile_2023-01-23_0000",
            "TestDir1" + os.sep + "TestFile11",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile11_2023-01-23_0000",
            "TestDir1" + os.sep + "TestFile12.ext",
            "TestDir1" + os.sep + ".old" + os.sep + "TestFile12_2023-01-23_0000.ext",
            "TestDir2" + os.sep + ".TestFile21",
            "TestDir2" + os.sep + ".old" + os.sep + ".TestFile21_2023-01-23_0000",
            "TestDir2" + os.sep + "TestFile22",
            "TestDir2" + os.sep + ".old" + os.sep + "TestFile22_2023-01-23_0000",
        ]
    )
    assert len(actual3) == len(expected_logs)
    for line, expected in zip(actual3, expected_logs):
        assert expected in line
