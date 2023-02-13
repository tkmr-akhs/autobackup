import pytest
import pytest_mock
import pytest_raises
import os
import sqlite3
import sys

from autobackup import bkup, dstrepo, fsutil, metarepo, scanner, srcrepo


def test_BackupFacade_get_update_list_ReturnRecordsToBeUpdated(
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
    actual = [found_file for found_file in fcd._get_backup_list(file_dict)]

    # Assert
    assert set(actual) == set([found_file2])


def test_BackupFacade_execute_Execute(mocker, FoundFileMock, AllFileScannerMock):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    mocker.patch("autobackup.scanner.AllFileScanner", new=AllFileScannerMock)
    actual_called = []
    actual_args = {}

    # STEP 1
    def _get_files_matching_criteria(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for key, value in x.items():
            if key == "1":
                actual_called.append(f"{co_name}[{key}]SKIP")
            else:
                actual_called.append(f"{co_name}[{key}]")
                yield (key, value)
        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.srcrepo.SourceRepository.get_files_matching_criteria",
        side_effect=_get_files_matching_criteria,
    )

    # STEP 2
    def _get_uncontained_keys(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for key in x:
            if key == "2":
                actual_called.append(f"{co_name}[{key}]SKIP")
            else:
                actual_called.append(f"{co_name}[{key}]")
                yield key
        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.metarepo.MetadataRepository.get_uncontained_keys",
        side_effect=_get_uncontained_keys,
    )

    # STEP 3
    def _remove_metadatas(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for key in x:
            actual_called.append(f"{co_name}[{key}]")
            yield metarepo.Metadata(key, 0.0)
        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.metarepo.MetadataRepository.remove_metadatas",
        side_effect=_remove_metadatas,
    )

    # STEP 4
    def __get_backup_list(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for key, value in x.items():
            if key == "4":
                actual_called.append(f"{co_name}[{key}]SKIP")
            else:
                actual_called.append(f"{co_name}[{key}]")
                yield value

        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.bkup.BackupFacade._get_backup_list",
        side_effect=__get_backup_list,
    )

    # STEP 5
    def _create_backups(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for item in x:
            if item.name == "5":
                actual_called.append(f"{co_name}[{item.name}]SKIP")
            else:
                actual_called.append(f"{co_name}[{item.name}]")
                yield (item, item)

        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.dstrepo.DestinationRepository.create_backups",
        side_effect=_create_backups,
    )

    # STEP 6
    def _update_metadata(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + f"[{os.path.basename(x.key)}]")
        return None

    mocker.patch(
        "autobackup.metarepo.MetadataRepository.update_metadata",
        side_effect=_update_metadata,
    )

    # STEP 7
    def _get_discard_list(*args, **kwargs):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (
            str(type(args[0]).__name__),
            str(type(kwargs["phase1_weeks"]).__name__),
            str(type(kwargs["phase2_months"]).__name__),
        )
        actual_called.append(co_name + "[yield start]")
        for i, _ in enumerate(args[0]):
            if i == 0:
                actual_called.append(f"{co_name}[{i}]")
                yield fsutil.FoundFile("7-0")
            elif i == 1:
                actual_called.append(f"{co_name}[{i}]")
                yield fsutil.FoundFile("7-1")
            elif i == 2:
                actual_called.append(f"{co_name}[{i}]")
                yield fsutil.FoundFile("7-2")
        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.dstrepo.DestinationRepository.get_discard_list",
        side_effect=_get_discard_list,
    )

    # STEP 8
    def _remove_backups(x):
        nonlocal actual_called
        nonlocal actual_args
        co_name = sys._getframe().f_code.co_name
        actual_args[co_name] = (str(type(x).__name__),)
        actual_called.append(co_name + "[yield start]")
        for item in x:
            if item.name == "7-1":
                actual_called.append(f"{co_name}[{item.name}]SKIP")
            else:
                actual_called.append(f"{co_name}[{item.name}]")
                yield item
        actual_called.append(co_name + "[yield finish]")

    mocker.patch(
        "autobackup.dstrepo.DestinationRepository.remove_backups",
        side_effect=_remove_backups,
    )

    # BackupFacade
    scnr = scanner.AllFileScanner(
        None,
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
    assert actual_called == [
        "_get_files_matching_criteria[yield start]",
        "_get_files_matching_criteria[0]",
        "_get_files_matching_criteria[1]SKIP",
        "_get_files_matching_criteria[2]",
        "_get_files_matching_criteria[3]",
        "_get_files_matching_criteria[4]",
        "_get_files_matching_criteria[5]",
        "_get_files_matching_criteria[6]",
        "_get_files_matching_criteria[yield finish]",
        "_remove_metadatas[yield start]",
        "_get_uncontained_keys[yield start]",
        "_get_uncontained_keys[0]",
        "_remove_metadatas[0]",
        "_get_uncontained_keys[2]SKIP",
        "_get_uncontained_keys[3]",
        "_remove_metadatas[3]",
        "_get_uncontained_keys[4]",
        "_remove_metadatas[4]",
        "_get_uncontained_keys[5]",
        "_remove_metadatas[5]",
        "_get_uncontained_keys[6]",
        "_remove_metadatas[6]",
        "_get_uncontained_keys[yield finish]",
        "_remove_metadatas[yield finish]",
        "_create_backups[yield start]",
        "__get_backup_list[yield start]",
        "__get_backup_list[0]",
        "_create_backups[0]",
        "_update_metadata[0]",
        "__get_backup_list[2]",
        "_create_backups[2]",
        "_update_metadata[2]",
        "__get_backup_list[3]",
        "_create_backups[3]",
        "_update_metadata[3]",
        "__get_backup_list[4]SKIP",
        "__get_backup_list[5]",
        "_create_backups[5]SKIP",
        "__get_backup_list[6]",
        "_create_backups[6]",
        "_update_metadata[6]",
        "__get_backup_list[yield finish]",
        "_create_backups[yield finish]",
        "_remove_backups[yield start]",
        "_get_discard_list[yield start]",
        "_get_discard_list[0]",
        "_remove_backups[7-0]",
        "_get_discard_list[1]",
        "_remove_backups[7-1]SKIP",
        "_get_discard_list[2]",
        "_remove_backups[7-2]",
        "_get_discard_list[yield finish]",
        "_remove_backups[yield finish]",
    ]
    assert actual_args == {
        "_get_files_matching_criteria": ("dict",),
        "_remove_metadatas": ("generator",),
        "_get_uncontained_keys": ("dict_keys",),
        "_create_backups": ("generator",),
        "__get_backup_list": ("dict",),
        "_update_metadata": ("Metadata",),
        "_remove_backups": ("generator",),
        "_get_discard_list": ("dict", "int", "int"),
    }
