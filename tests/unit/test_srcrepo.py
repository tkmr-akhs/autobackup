import pytest
import pytest_mock
import pytest_raises
from logging import DEBUG, ERROR, INFO, WARNING
from os import sep

from autobackup import scanner, srcrepo


class Test_SourceRepository_get_files_matching_criteria:
    @staticmethod
    def test_IfTragetDirThenReturnFoundFileInfoDict(dummy_testdata, build_path):
        target_path, all_files = dummy_testdata
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

        s_repo = srcrepo.SourceRepository(
            None,
            targets,
            ".old",
        )

        file_list = dict(s_repo.get_files_matching_criteria(all_files))

        actual1 = len(file_list)
        actual2 = str(file_list[key1].relpath)
        actual3 = str(file_list[key2].relpath)

        assert actual1 == 2
        assert actual2 == "TestDir1" + sep + "TestFile11"
        assert actual3 == "TestDir1" + sep + "TestFile12.ext"

    @staticmethod
    def test_IfTragetDirAndFilteredThenReturnFoundFileInfoDict(
        dummy_testdata, build_path
    ):
        target_path, all_files = dummy_testdata
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

        s_repo = srcrepo.SourceRepository(None, targets, ".old")
        file_list = dict(s_repo.get_files_matching_criteria(all_files))

        actual1 = len(file_list)
        actual2 = str(file_list[key].relpath)

        assert actual1 == 1
        assert actual2 == "TestDir1" + sep + "TestFile12.ext"

    @staticmethod
    def test_IfTragetDirAndIgnoreHiddenFileThenReturnFoundFileInfoDict(
        dummy_testdata, build_path
    ):
        target_path, all_files = dummy_testdata
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

        s_repo = srcrepo.SourceRepository(
            None,
            targets,
            ".old",
        )
        file_list = dict(s_repo.get_files_matching_criteria(all_files))

        actual1 = len(file_list)
        actual2 = str(file_list[key].relpath)

        assert actual1 == 1
        assert actual2 == "TestDir2" + sep + "TestFile22"

    @staticmethod
    def test_IfTragetDirThenReturnEmptyDict(dummy_testdata, build_path):
        target_path, all_files = dummy_testdata
        targets = [
            {
                "path": target_path,
                "catch_regex": "hoge",
                "ignore_regex": "",
                "catch_hidden": True,
                "catch_link": True,
            }
        ]
        s_repo = srcrepo.SourceRepository(
            None,
            targets,
            ".old",
        )
        file_list = dict(s_repo.get_files_matching_criteria(all_files))

        actual = len(file_list)

        assert actual == 0

    @staticmethod
    def test_SkipDstDir(caplog, dummy_testdata_fresh, build_path):
        # Arrange
        caplog.set_level(DEBUG)
        expected_logs = [
            ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
            ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
            ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
            ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
            ("autobackup.srcrepo", DEBUG, "NOT_SRC(BkupDir): "),
        ]

        target_path, all_files = dummy_testdata_fresh

        targets = [
            {
                "path": target_path,
                "catch_regex": ".*",
                "ignore_regex": "",
                "catch_hidden": True,
                "catch_link": True,
            }
        ]

        s_repo = srcrepo.SourceRepository(None, targets, ".old")

        # Act
        actual1 = [
            str(file.relpath)
            for file in dict(s_repo.get_files_matching_criteria(all_files)).values()
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
