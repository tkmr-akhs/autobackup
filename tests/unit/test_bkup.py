import pytest
import pytest_mock
import pytest_raises
import datetime
import sqlite3
import sys
from os import sep

from autobackup import bkup, dstrepo, fsutil, metarepo, scanner, srcrepo


class Test_BackupFacade_get_uncontained_keys:
    @staticmethod
    def test_ReturnRecordsToBeRemoved():
        # Arrange
        dbconn = sqlite3.connect(":memory:")
        m_repo = metarepo.MetadataRepository(dbconn)
        cur = dbconn.cursor()
        cur.execute(
            f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
                VALUES ('/path/to/file1.ext',0.0)"
        )
        cur.execute(
            f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
                VALUES ('/path/to/file2.ext',0.0)"
        )
        dbconn.commit()

        new_info = {"/path/to/file1.ext": None}

        fcd = bkup.BackupFacade(None, None, m_repo, None)

        # Act
        actual = [(item) for item in fcd._get_uncontained_keys(new_info.keys())]

        # Assert
        assert set(actual) == set(["/path/to/file2.ext"])


class Test_BackupFacade_get_files_to_be_discarded:
    @staticmethod
    def test_IfFileInfoIsEmptyThenReturnEmptyList():
        # Arrange
        today = datetime.date(2023, 1, 22)
        d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
        all_files = {}

        fcd = bkup.BackupFacade(None, d_repo, None, None)

        # Act
        actual = [
            item for item in fcd._get_files_to_be_discarded(all_files, today, 2, 2)
        ]

        # Assert
        assert actual == []

    @staticmethod
    def test_IfNotBackupedFileThenNotContainIt(mocker, FoundFileMock):
        # Arrange
        mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
        today = datetime.date(2023, 1, 22)
        path0 = "path_to_dir" + sep + "file_2000-01-01_0000.txt"
        path0_mtime = datetime.datetime(2000, 1, 1, 1, 0, 0, 0).timestamp()

        d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

        all_files = {path0: fsutil.FoundFile(path0, None, path0_mtime)}

        fcd = bkup.BackupFacade(None, d_repo, None, None)

        # Act
        actual = [
            item for item in fcd._get_files_to_be_discarded(all_files, today, 2, 2)
        ]

        # Assert
        assert actual == []

    @staticmethod
    def test_ReturnCorrectList(
        test_prarams_for_get_discard_list,
    ):
        # Arrange
        # mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
        today, all_files, expected = test_prarams_for_get_discard_list
        d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
        fcd = bkup.BackupFacade(None, d_repo, None, None)

        # Act
        actual = [
            item for item in fcd._get_files_to_be_discarded(all_files, today, 2, 2)
        ]

        # Assert
        assert set(actual) == set(expected)

    @staticmethod
    def test_IfSeqNumFlagIsDisabledThenReturnDiscardList(
        mocker, FoundFileMock, build_path
    ):
        # Arrange
        mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
        today = datetime.date(2023, 1, 22)
        d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", None)
        path0 = build_path("path_to_dir", ".old", file="File_2022-12-31.txt")
        path1 = build_path("path_to_dir", ".old", file="File_2023-01-01.txt")
        path0_mtime = datetime.datetime(2023, 1, 1, 0, 0, 0, 0).timestamp()
        path1_mtime = datetime.datetime(2023, 1, 1, 1, 0, 0, 0).timestamp()
        path0_obj = fsutil.FoundFile(path0, None, path0_mtime)
        path1_obj = fsutil.FoundFile(path1, None, path1_mtime)
        all_files = {path0: path0_obj, path1: path1_obj}
        expected = [path0_obj]

        fcd = bkup.BackupFacade(None, d_repo, None, None)

        # Act
        actual = [
            item for item in fcd._get_files_to_be_discarded(all_files, today, 2, 2)
        ]

        # Assert
        assert set(actual) == set(expected)


class Test_BackupFacade_get_modified_files:
    @staticmethod
    def test_ReturnRecordsToBeUpdated(
        mocker, FoundFileMock, AllFileScannerMock, build_path
    ):
        # Arrange
        mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
        mocker.patch("autobackup.scanner.AllFileScanner", new=AllFileScannerMock)

        dbconn = sqlite3.connect(":memory:")
        m_repo = metarepo.MetadataRepository(dbconn)
        cur = dbconn.cursor()
        cur.execute(
            f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
                VALUES ('{build_path('/path/to', file='file1.ext')}',{1.0})"
        )
        cur.execute(
            f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
                VALUES ('{build_path('/path/to', file='file2.ext')}',{0.0})"
        )
        dbconn.commit()

        found_file1 = fsutil.FoundFile("/path/to/file1.ext", None, 1.0)
        found_file2 = fsutil.FoundFile("/path/to/file2.ext", None, 1.0)
        file_dict = {
            found_file1.normpath_str: found_file1,
            found_file2.normpath_str: found_file2,
        }

        fcd = bkup.BackupFacade(None, None, m_repo, None)

        # Act
        actual = [found_file for found_file in fcd._get_modified_files(file_dict)]

        # Assert
        assert set(actual) == set([found_file2])


class Test_BackupFacade_execute:
    @staticmethod
    def test_Execute(mocker, FoundFileMock, AllFileScannerMock):
        from os.path import basename

        # Arrange
        mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
        mocker.patch("autobackup.scanner.AllFileScanner", new=AllFileScannerMock)
        actual_called = {}
        actual_called_skip = {}
        actual_args = {}

        # STEP 1
        def _get_files_matching_criteria(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for key, value in x.items():
                if key == "1":
                    actual_called_skip[co_name] += 1
                else:
                    actual_called[co_name] += 1
                    yield (key, value)

        mocker.patch(
            "autobackup.srcrepo.SourceRepository.get_files_matching_criteria",
            side_effect=_get_files_matching_criteria,
        )

        # STEP 2
        def _get_uncontained_keys(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for key in x:
                if key == "2":
                    actual_called_skip[co_name] += 1
                else:
                    actual_called[co_name] += 1
                    yield key

        mocker.patch(
            "autobackup.bkup.BackupFacade._get_uncontained_keys",
            side_effect=_get_uncontained_keys,
        )

        # STEP 3
        def _remove_metadatas(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for key in x:
                actual_called[co_name] += 1
                yield metarepo.Metadata(key, 0.0)

        mocker.patch(
            "autobackup.metarepo.MetadataRepository.remove_metadatas",
            side_effect=_remove_metadatas,
        )

        # STEP 4
        def _get_modified_files(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for key, value in x.items():
                if key == "4":
                    actual_called_skip[co_name] += 1
                else:
                    actual_called[co_name] += 1
                    yield value

        mocker.patch(
            "autobackup.bkup.BackupFacade._get_modified_files",
            side_effect=_get_modified_files,
        )

        # STEP 5
        def _create_backups(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for item in x:
                if item.name == "5":
                    actual_called_skip[co_name] += 1
                else:
                    actual_called[co_name] += 1
                    yield (item, item)

        mocker.patch(
            "autobackup.dstrepo.DestinationRepository.create_backups",
            side_effect=_create_backups,
        )

        # STEP 6
        def _update_metadata(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            actual_called[co_name] += 1
            return None

        mocker.patch(
            "autobackup.metarepo.MetadataRepository.update_metadata",
            side_effect=_update_metadata,
        )

        # STEP 7
        def _get_files_to_be_discarded(*args, **kwargs):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (
                str(type(args[0]).__name__),
                str(type(kwargs["phase1_weeks"]).__name__),
                str(type(kwargs["phase2_months"]).__name__),
            )
            for i, _ in enumerate(args[0]):
                if i == 0:
                    actual_called[co_name] += 1
                    yield fsutil.FoundFile("7-0")
                elif i == 1:
                    actual_called[co_name] += 1
                    yield fsutil.FoundFile("7-1")
                elif i == 2:
                    actual_called[co_name] += 1
                    yield fsutil.FoundFile("7-2")

        mocker.patch(
            "autobackup.bkup.BackupFacade._get_files_to_be_discarded",
            side_effect=_get_files_to_be_discarded,
        )

        # STEP 8
        def _remove_backups(x):
            nonlocal actual_called
            nonlocal actual_called_skip
            nonlocal actual_args
            co_name = sys._getframe().f_code.co_name
            actual_called[co_name] = (
                0 if not co_name in actual_called.keys() else actual_called[co_name]
            )
            actual_called_skip[co_name] = (
                0
                if not co_name in actual_called_skip.keys()
                else actual_called_skip[co_name]
            )
            actual_args[co_name] = (str(type(x).__name__),)
            for item in x:
                if item.name == "7-1":
                    actual_called_skip[co_name] += 1
                else:
                    actual_called[co_name] += 1
                    yield item

        mocker.patch(
            "autobackup.dstrepo.DestinationRepository.remove_backups",
            side_effect=_remove_backups,
        )

        # BackupFacade
        scnr = scanner.AllFileScanner(
            None,
            False,
            {
                "0": fsutil.FoundFile("0"),
                "1": fsutil.FoundFile("1"),
                "2": fsutil.FoundFile("2"),
                "3": fsutil.FoundFile("3"),
                "4": fsutil.FoundFile("4"),
                "5": fsutil.FoundFile("5"),
                "6": fsutil.FoundFile("6"),
            },
        )
        fcd = bkup.BackupFacade(
            srcrepo.SourceRepository(
                None,
                [
                    {
                        "path": "0",
                        "catch_regex": ".*",
                        "ignore_regex": "",
                        "catch_hidden": False,
                        "catch_link": False,
                    }
                ],
                None,
            ),
            dstrepo.DestinationRepository(None, "", "", ""),
            metarepo.MetadataRepository(sqlite3.connect(":memory:")),
            scnr,
        )

        # Act
        fcd.execute()

        # Assert
        assert actual_called == {
            "_get_files_matching_criteria": 6,
            "_remove_metadatas": 5,
            "_get_uncontained_keys": 5,
            "_create_backups": 4,
            "_get_modified_files": 5,
            "_update_metadata": 4,
            "_remove_backups": 2,
            "_get_files_to_be_discarded": 3,
        }
        assert actual_called_skip == {
            "_get_files_matching_criteria": 1,
            "_remove_metadatas": 0,
            "_get_uncontained_keys": 1,
            "_create_backups": 1,
            "_get_modified_files": 1,
            "_update_metadata": 0,
            "_remove_backups": 1,
            "_get_files_to_be_discarded": 0,
        }
        assert actual_args == {
            "_get_files_matching_criteria": ("dict",),
            "_remove_metadatas": ("generator",),
            "_get_uncontained_keys": ("dict_keys",),
            "_create_backups": ("generator",),
            "_get_modified_files": ("dict",),
            "_update_metadata": ("Metadata",),
            "_remove_backups": ("generator",),
            "_get_files_to_be_discarded": ("dict", "int", "int"),
        }
