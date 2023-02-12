import pytest
import pytest_mock
import pytest_raises
from logging import DEBUG, ERROR, INFO, WARNING
from os import sep

from autobackup import scanner, srcrepo


def test_SourceRepository_get_current_files_IfTragetDirThenReturnFoundFileInfoDict(
    testdata, build_path
):
    target_path = testdata(__name__)
    key1 = build_path(target_path, "testdir1", file="testfile11")
    key2 = build_path(target_path, "testdir1", file="testfile12.ext")

    targets = [
        {
            "path": target_path,
            "catch_regex": ".*TestFile1.*",
            "ignore_regex": "",
            "catch_hidden": True,
            "catch_link": True,
        }
    ]

    scnr = srcrepo.SourceRepository(
        scanner.AllFileScanner(targets),
        targets,
        ".old",
    )

    file_list = dict(scnr.get_files_matching_criteria())

    actual1 = len(file_list)
    actual2 = str(file_list[key1].relpath)
    actual3 = str(file_list[key2].relpath)

    assert actual1 == 2
    assert actual2 == "TestDir1" + sep + "TestFile11"
    assert actual3 == "TestDir1" + sep + "TestFile12.ext"


def test_SourceRepository_get_current_files_IfTragetDirAndFilteredThenReturnFoundFileInfoDict(
    testdata, build_path
):
    target_path = testdata(__name__)
    key = build_path(target_path, "testdir1", file="testfile12.ext")
    targets = [
        {
            "path": target_path,
            "catch_regex": ".*TestFile1.*",
            "ignore_regex": ".*TestFile11",
            "catch_hidden": True,
            "catch_link": True,
        }
    ]

    scnr = srcrepo.SourceRepository(scanner.AllFileScanner(targets), targets, ".old")
    file_list = dict(scnr.get_files_matching_criteria())

    actual1 = len(file_list)
    actual2 = str(file_list[key].relpath)

    assert actual1 == 1
    assert actual2 == "TestDir1" + sep + "TestFile12.ext"


def test_SourceRepository_get_current_files_IfTragetDirAndIgnoreHiddenFileThenReturnFoundFileInfoDict(
    testdata, build_path
):
    target_path = testdata(__name__)
    key = build_path(target_path, "testdir2", file="testfile22")
    targets = [
        {
            "path": target_path,
            "catch_regex": ".*TestFile2.*",
            "ignore_regex": "",
            "catch_hidden": False,
            "catch_link": True,
        }
    ]

    scnr = srcrepo.SourceRepository(
        scanner.AllFileScanner(targets),
        targets,
        ".old",
    )
    file_list = dict(scnr.get_files_matching_criteria())

    actual1 = len(file_list)
    actual2 = str(file_list[key].relpath)

    assert actual1 == 1
    assert actual2 == "TestDir2" + sep + "TestFile22"


def test_SourceRepository_get_current_files_IfTragetDirThenReturnEmptyDict(
    testdata, build_path
):
    target_path = testdata(__name__)
    targets = [
        {
            "path": target_path,
            "catch_regex": "hoge",
            "ignore_regex": "",
            "catch_hidden": True,
            "catch_link": True,
        }
    ]
    scnr = srcrepo.SourceRepository(
        scanner.AllFileScanner(targets),
        targets,
        ".old",
    )
    file_list = dict(scnr.get_files_matching_criteria())

    actual = len(file_list)

    assert actual == 0


def test_SourceRepository_get_current_files_SkipDstDir(
    caplog, testdata_fresh, build_path
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
        ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
        ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
        ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
        ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
    ]

    target_root = testdata_fresh(__name__)

    targets = [
        {
            "path": target_root,
            "catch_regex": ".*",
            "ignore_regex": "",
            "catch_hidden": True,
            "catch_link": True,
        }
    ]

    s_repo = srcrepo.SourceRepository(scanner.AllFileScanner(targets), targets, ".old")

    # Act
    actual1 = [
        str(file.relpath)
        for file in dict(s_repo.get_files_matching_criteria()).values()
    ]
    actual2 = caplog.record_tuples

    # Assert
    assert set(actual1) == set(
        [
            "TestFile",
            "TestDir1" + sep + "TestFile11",
            "TestDir1" + sep + "TestFile12.ext",
            "TestDir2" + sep + ".TestFile21",
            "TestDir2" + sep + "TestFile22",
        ]
    )
    assert len(actual2) == len(expected_logs)
    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual2, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)
