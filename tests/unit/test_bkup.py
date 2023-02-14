import pytest
import pytest_mock
import pytest_raises
import datetime
import os
import sqlite3
import sys

from tests.testutil import build_path

from collections.abc import Generator
from os import sep
from autobackup import bkup, dstrepo, fsutil, metarepo, scanner, srcrepo


def test_BackupFacade_get_inexistent_metadatas_ReturnRecordsToBeRemoved():
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


def test_BackupFacade_get_discard_list_IfFileInfoIsEmptyThenReturnEmptyList():
    # Arrange
    today = datetime.date(2023, 1, 22)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    all_files = {}

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert actual == []


def test_BackupFacade_get_discard_list_IfNotBackupedFileThenNotContainIt(
    mocker, FoundFileMock
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 22)
    path0 = "path_to_dir" + sep + "file_2000-01-01_0000.txt"
    path0_mtime = datetime.datetime(2000, 1, 1, 1, 0, 0, 0).timestamp()

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    all_files = {path0: fsutil.FoundFile(path0, None, path0_mtime)}

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert actual == []


def test_BackupFacade_get_discard_list_Phase1Test(test_prarams_for_get_discard_list):
    # Arrange
    # mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today, all_files, expected = test_prarams_for_get_discard_list
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


def test_BackupFacade_get_discard_list_IfFileInfoIsPhase1ThenReturnDiscardList(
    mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 22)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    path0 = build_path("path_to_dir", ".old", file="File_2022-12-31_0000.txt")
    path1 = build_path("path_to_dir", ".old", file="File_2022-12-31_0002.txt")
    path2 = build_path("path_to_dir", ".old", file="File_2022-12-31_0001.txt")
    path3 = build_path("path_to_dir", ".old", file="File_2023-01-01_0000.txt")
    path4 = build_path("path_to_dir", ".old", file="File_2023-01-01_0001.txt")
    path5 = build_path("path_to_dir", ".old", file="File_2023-01-01_0002.txt")
    path6 = build_path("path_to_dir", ".old", file="File_2023-01-02_0000.txt")
    path7 = build_path("path_to_dir", ".old", file="File_2023-01-02_0001.txt")
    path8 = build_path("path_to_dir", ".old", file="File_2023-01-02_0002.txt")
    path9 = build_path("path_to_dir", ".old", file="File_2023-01-03_0000.txt")
    path10 = build_path("path_to_dir", ".old", file="File_2023-01-03_0001.txt")
    path11 = build_path("path_to_dir", ".old", file="File_2023-01-03_0002.txt")

    path0_mtime = datetime.datetime(2022, 12, 31, 1, 0, 0, 0).timestamp()
    path1_mtime = datetime.datetime(2022, 12, 31, 3, 0, 0, 0).timestamp()
    path2_mtime = datetime.datetime(2022, 12, 31, 2, 0, 0, 0).timestamp()
    path3_mtime = datetime.datetime(2023, 1, 1, 1, 0, 0, 0).timestamp()
    path4_mtime = datetime.datetime(2023, 1, 1, 2, 0, 0, 0).timestamp()
    path5_mtime = datetime.datetime(2023, 1, 1, 3, 0, 0, 0).timestamp()
    path6_mtime = datetime.datetime(2023, 1, 2, 1, 0, 0, 0).timestamp()
    path7_mtime = datetime.datetime(2023, 1, 2, 2, 0, 0, 0).timestamp()
    path8_mtime = datetime.datetime(2023, 1, 2, 3, 0, 0, 0).timestamp()
    path9_mtime = datetime.datetime(2023, 1, 3, 1, 0, 0, 0).timestamp()
    path10_mtime = datetime.datetime(2023, 1, 3, 2, 0, 0, 0).timestamp()
    path11_mtime = datetime.datetime(2023, 1, 3, 3, 0, 0, 0).timestamp()

    path0_obj = fsutil.FoundFile(path0, None, path0_mtime)
    path1_obj = fsutil.FoundFile(path1, None, path1_mtime)
    path2_obj = fsutil.FoundFile(path2, None, path2_mtime)
    path3_obj = fsutil.FoundFile(path3, None, path3_mtime)
    path4_obj = fsutil.FoundFile(path4, None, path4_mtime)
    path5_obj = fsutil.FoundFile(path5, None, path5_mtime)
    path6_obj = fsutil.FoundFile(path6, None, path6_mtime)
    path7_obj = fsutil.FoundFile(path7, None, path7_mtime)
    path8_obj = fsutil.FoundFile(path8, None, path8_mtime)
    path9_obj = fsutil.FoundFile(path9, None, path9_mtime)
    path10_obj = fsutil.FoundFile(path10, None, path10_mtime)
    path11_obj = fsutil.FoundFile(path11, None, path11_mtime)

    all_files = {
        path0: path0_obj,
        path1: path1_obj,
        path2: path2_obj,
        path3: path3_obj,
        path4: path4_obj,
        path5: path5_obj,
        path6: path6_obj,
        path7: path7_obj,
        path8: path8_obj,
        path9: path9_obj,
        path10: path10_obj,
        path11: path11_obj,
    }
    expected = [path0_obj, path2_obj, path3_obj, path4_obj]

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


def test_BackupFacade_get_discard_list_IfFileInfoIsPhase1ThenReturnDiscardList_2(
    mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 23)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    path0 = build_path("path_to_dir", ".old", file="File_2023-01-07_0000.txt")
    path1 = build_path("path_to_dir", ".old", file="File_2023-01-07_0001.txt")
    path2 = build_path("path_to_dir", ".old", file="File_2023-01-07_0002.txt")
    path3 = build_path("path_to_dir", ".old", file="File_2023-01-08_0000.txt")
    path4 = build_path("path_to_dir", ".old", file="File_2023-01-08_0001.txt")
    path5 = build_path("path_to_dir", ".old", file="File_2023-01-08_0002.txt")
    path6 = build_path("path_to_dir", ".old", file="File_2023-01-09_0000.txt")
    path7 = build_path("path_to_dir", ".old", file="File_2023-01-09_0001.txt")
    path8 = build_path("path_to_dir", ".old", file="File_2023-01-09_0002.txt")
    path9 = build_path("path_to_dir", ".old", file="File_2023-01-10_0000.txt")
    path10 = build_path("path_to_dir", ".old", file="File_2023-01-10_0001.txt")
    path11 = build_path("path_to_dir", ".old", file="File_2023-01-10_0002.txt")

    path0_mtime = datetime.datetime(2023, 1, 7, 1, 0, 0, 0).timestamp()
    path1_mtime = datetime.datetime(2023, 1, 7, 2, 0, 0, 0).timestamp()
    path2_mtime = datetime.datetime(2023, 1, 7, 3, 0, 0, 0).timestamp()
    path3_mtime = datetime.datetime(2023, 1, 8, 1, 0, 0, 0).timestamp()
    path4_mtime = datetime.datetime(2023, 1, 8, 2, 0, 0, 0).timestamp()
    path5_mtime = datetime.datetime(2023, 1, 8, 3, 0, 0, 0).timestamp()
    path6_mtime = datetime.datetime(2023, 1, 9, 1, 0, 0, 0).timestamp()
    path7_mtime = datetime.datetime(2023, 1, 9, 2, 0, 0, 0).timestamp()
    path8_mtime = datetime.datetime(2023, 1, 9, 3, 0, 0, 0).timestamp()
    path9_mtime = datetime.datetime(2023, 1, 10, 1, 0, 0, 0).timestamp()
    path10_mtime = datetime.datetime(2023, 1, 10, 2, 0, 0, 0).timestamp()
    path11_mtime = datetime.datetime(2023, 1, 10, 3, 0, 0, 0).timestamp()

    path0_obj = fsutil.FoundFile(path0, None, path0_mtime)
    path1_obj = fsutil.FoundFile(path1, None, path1_mtime)
    path2_obj = fsutil.FoundFile(path2, None, path2_mtime)
    path3_obj = fsutil.FoundFile(path3, None, path3_mtime)
    path4_obj = fsutil.FoundFile(path4, None, path4_mtime)
    path5_obj = fsutil.FoundFile(path5, None, path5_mtime)
    path6_obj = fsutil.FoundFile(path6, None, path6_mtime)
    path7_obj = fsutil.FoundFile(path7, None, path7_mtime)
    path8_obj = fsutil.FoundFile(path8, None, path8_mtime)
    path9_obj = fsutil.FoundFile(path9, None, path9_mtime)
    path10_obj = fsutil.FoundFile(path10, None, path10_mtime)
    path11_obj = fsutil.FoundFile(path11, None, path11_mtime)

    all_files = {
        path0: path0_obj,
        path1: path1_obj,
        path2: path2_obj,
        path3: path3_obj,
        path4: path4_obj,
        path5: path5_obj,
        path6: path6_obj,
        path7: path7_obj,
        path8: path8_obj,
        path9: path9_obj,
        path10: path10_obj,
        path11: path11_obj,
    }
    expected = [path0_obj, path1_obj, path3_obj, path4_obj]

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


def test_BackupFacade_get_discard_list_IfFileInfoIsPhase2ThenReturnDiscardList(
    mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 22)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    path0 = build_path("path_to_dir", ".old", file="File_2022-10-23_0000.txt")
    path1 = build_path("path_to_dir", ".old", file="File_2022-10-22_0001.txt")
    path2 = build_path("path_to_dir", ".old", file="File_2022-10-24_0002.txt")
    path3 = build_path("path_to_dir", ".old", file="File_2022-10-29_0000.txt")
    path4 = build_path("path_to_dir", ".old", file="File_2022-10-30_0001.txt")
    path5 = build_path("path_to_dir", ".old", file="File_2022-10-30_0002.txt")
    path6 = build_path("path_to_dir", ".old", file="File_2022-10-31_0000.txt")
    path7 = build_path("path_to_dir", ".old", file="File_2022-10-31_0001.txt")
    path8 = build_path("path_to_dir", ".old", file="File_2022-10-31_0002.txt")
    path9 = build_path("path_to_dir", ".old", file="File_2022-11-01_0000.txt")
    path10 = build_path("path_to_dir", ".old", file="File_2022-11-01_0001.txt")
    path11 = build_path("path_to_dir", ".old", file="File_2022-11-01_0002.txt")
    path12 = build_path("path_to_dir", ".old", file="File_2022-11-02_0000.txt")
    path13 = build_path("path_to_dir", ".old", file="File_2022-11-02_0001.txt")
    path14 = build_path("path_to_dir", ".old", file="File_2022-11-02_0002.txt")

    path0_mtime = datetime.datetime(2022, 10, 23, 1, 0, 0, 0).timestamp()
    path1_mtime = datetime.datetime(2022, 10, 22, 2, 0, 0, 0).timestamp()
    path2_mtime = datetime.datetime(2022, 10, 24, 3, 0, 0, 0).timestamp()
    path3_mtime = datetime.datetime(2022, 10, 28, 1, 0, 0, 0).timestamp()
    path4_mtime = datetime.datetime(2022, 10, 29, 2, 0, 0, 0).timestamp()
    path5_mtime = datetime.datetime(2022, 10, 30, 3, 0, 0, 0).timestamp()
    path6_mtime = datetime.datetime(2022, 10, 31, 1, 0, 0, 0).timestamp()
    path7_mtime = datetime.datetime(2022, 10, 31, 2, 0, 0, 0).timestamp()
    path8_mtime = datetime.datetime(2022, 10, 31, 3, 0, 0, 0).timestamp()
    path9_mtime = datetime.datetime(2022, 11, 1, 1, 0, 0, 0).timestamp()
    path10_mtime = datetime.datetime(2022, 11, 1, 2, 0, 0, 0).timestamp()
    path11_mtime = datetime.datetime(2022, 11, 1, 3, 0, 0, 0).timestamp()
    path12_mtime = datetime.datetime(2022, 11, 2, 1, 0, 0, 0).timestamp()
    path13_mtime = datetime.datetime(2022, 11, 2, 2, 0, 0, 0).timestamp()
    path14_mtime = datetime.datetime(2022, 11, 2, 3, 0, 0, 0).timestamp()

    path0_obj = fsutil.FoundFile(path0, None, path0_mtime)
    path1_obj = fsutil.FoundFile(path1, None, path1_mtime)
    path2_obj = fsutil.FoundFile(path2, None, path2_mtime)
    path3_obj = fsutil.FoundFile(path3, None, path3_mtime)
    path4_obj = fsutil.FoundFile(path4, None, path4_mtime)
    path5_obj = fsutil.FoundFile(path5, None, path5_mtime)
    path6_obj = fsutil.FoundFile(path6, None, path6_mtime)
    path7_obj = fsutil.FoundFile(path7, None, path7_mtime)
    path8_obj = fsutil.FoundFile(path8, None, path8_mtime)
    path9_obj = fsutil.FoundFile(path9, None, path9_mtime)
    path10_obj = fsutil.FoundFile(path10, None, path10_mtime)
    path11_obj = fsutil.FoundFile(path11, None, path11_mtime)
    path12_obj = fsutil.FoundFile(path11, None, path12_mtime)
    path13_obj = fsutil.FoundFile(path11, None, path13_mtime)
    path14_obj = fsutil.FoundFile(path11, None, path14_mtime)

    all_files = {
        path0: path0_obj,
        path1: path1_obj,
        path2: path2_obj,
        path3: path3_obj,
        path4: path4_obj,
        path5: path5_obj,
        path6: path6_obj,
        path7: path7_obj,
        path8: path8_obj,
        path9: path9_obj,
        path10: path10_obj,
        path11: path11_obj,
        path12: path12_obj,
        path13: path13_obj,
        path14: path14_obj,
    }
    expected = [
        path1_obj,
        path2_obj,
        path3_obj,
        path4_obj,
        path6_obj,
        path7_obj,
        path9_obj,
        path10_obj,
        path12_obj,
        path13_obj,
    ]

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


def test_BackupFacade_get_discard_list_IfFileInfoIsPhase2ThenReturnDiscardList_2(
    mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 23)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    path0 = build_path("path_to_dir", ".old", file="File_2022-10-22_0000.txt")
    path1 = build_path("path_to_dir", ".old", file="File_2022-10-23_0001.txt")
    path2 = build_path("path_to_dir", ".old", file="File_2022-10-24_0002.txt")
    path3 = build_path("path_to_dir", ".old", file="File_2022-10-29_0000.txt")
    path4 = build_path("path_to_dir", ".old", file="File_2022-10-30_0001.txt")
    path5 = build_path("path_to_dir", ".old", file="File_2022-10-30_0002.txt")
    path6 = build_path("path_to_dir", ".old", file="File_2022-10-31_0000.txt")
    path7 = build_path("path_to_dir", ".old", file="File_2022-10-31_0001.txt")
    path8 = build_path("path_to_dir", ".old", file="File_2022-10-31_0002.txt")
    path9 = build_path("path_to_dir", ".old", file="File_2022-11-01_0000.txt")
    path10 = build_path("path_to_dir", ".old", file="File_2022-11-01_0001.txt")
    path11 = build_path("path_to_dir", ".old", file="File_2022-11-01_0002.txt")
    path12 = build_path("path_to_dir", ".old", file="File_2022-11-02_0000.txt")
    path13 = build_path("path_to_dir", ".old", file="File_2022-11-02_0001.txt")
    path14 = build_path("path_to_dir", ".old", file="File_2022-11-02_0002.txt")

    path0_mtime = datetime.datetime(2022, 10, 22, 1, 0, 0, 0).timestamp()
    path1_mtime = datetime.datetime(2022, 10, 23, 2, 0, 0, 0).timestamp()
    path2_mtime = datetime.datetime(2022, 10, 24, 3, 0, 0, 0).timestamp()
    path3_mtime = datetime.datetime(2022, 10, 28, 1, 0, 0, 0).timestamp()
    path4_mtime = datetime.datetime(2022, 10, 29, 2, 0, 0, 0).timestamp()
    path5_mtime = datetime.datetime(2022, 10, 30, 3, 0, 0, 0).timestamp()
    path6_mtime = datetime.datetime(2022, 10, 31, 1, 0, 0, 0).timestamp()
    path7_mtime = datetime.datetime(2022, 10, 31, 2, 0, 0, 0).timestamp()
    path8_mtime = datetime.datetime(2022, 10, 31, 3, 0, 0, 0).timestamp()
    path9_mtime = datetime.datetime(2022, 11, 1, 1, 0, 0, 0).timestamp()
    path10_mtime = datetime.datetime(2022, 11, 1, 2, 0, 0, 0).timestamp()
    path11_mtime = datetime.datetime(2022, 11, 1, 3, 0, 0, 0).timestamp()
    path12_mtime = datetime.datetime(2022, 11, 2, 1, 0, 0, 0).timestamp()
    path13_mtime = datetime.datetime(2022, 11, 2, 2, 0, 0, 0).timestamp()
    path14_mtime = datetime.datetime(2022, 11, 2, 3, 0, 0, 0).timestamp()

    path0_obj = fsutil.FoundFile(path0, None, path0_mtime)
    path1_obj = fsutil.FoundFile(path1, None, path1_mtime)
    path2_obj = fsutil.FoundFile(path2, None, path2_mtime)
    path3_obj = fsutil.FoundFile(path3, None, path3_mtime)
    path4_obj = fsutil.FoundFile(path4, None, path4_mtime)
    path5_obj = fsutil.FoundFile(path5, None, path5_mtime)
    path6_obj = fsutil.FoundFile(path6, None, path6_mtime)
    path7_obj = fsutil.FoundFile(path7, None, path7_mtime)
    path8_obj = fsutil.FoundFile(path8, None, path8_mtime)
    path9_obj = fsutil.FoundFile(path9, None, path9_mtime)
    path10_obj = fsutil.FoundFile(path10, None, path10_mtime)
    path11_obj = fsutil.FoundFile(path11, None, path11_mtime)
    path12_obj = fsutil.FoundFile(path11, None, path12_mtime)
    path13_obj = fsutil.FoundFile(path11, None, path13_mtime)
    path14_obj = fsutil.FoundFile(path11, None, path14_mtime)

    all_files = {
        path0: path0_obj,
        path1: path1_obj,
        path2: path2_obj,
        path3: path3_obj,
        path4: path4_obj,
        path5: path5_obj,
        path6: path6_obj,
        path7: path7_obj,
        path8: path8_obj,
        path9: path9_obj,
        path10: path10_obj,
        path11: path11_obj,
        path12: path12_obj,
        path13: path13_obj,
        path14: path14_obj,
    }
    expected = [
        path0_obj,
        path2_obj,
        path3_obj,
        path4_obj,
        path6_obj,
        path7_obj,
        path9_obj,
        path10_obj,
        path12_obj,
        path13_obj,
    ]

    fcd = bkup.BackupFacade(None, d_repo, None, None)

    # Act
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


def test_BackupFacade_get_discard_list_IfSeqNumFlagIsDisabledThenReturnDiscardList(
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
    actual = [item for item in fcd._get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert set(actual) == set(expected)


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
    def _get_backup_list(x):
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
        "autobackup.bkup.BackupFacade._get_backup_list",
        side_effect=_get_backup_list,
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
    def _get_discard_list(*args, **kwargs):
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
        "autobackup.bkup.BackupFacade._get_discard_list",
        side_effect=_get_discard_list,
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
        "_get_backup_list": 5,
        "_update_metadata": 4,
        "_remove_backups": 2,
        "_get_discard_list": 3,
    }
    assert actual_called_skip == {
        "_get_files_matching_criteria": 1,
        "_remove_metadatas": 0,
        "_get_uncontained_keys": 1,
        "_create_backups": 1,
        "_get_backup_list": 1,
        "_update_metadata": 0,
        "_remove_backups": 1,
        "_get_discard_list": 0,
    }
    assert actual_args == {
        "_get_files_matching_criteria": ("dict",),
        "_remove_metadatas": ("generator",),
        "_get_uncontained_keys": ("dict_keys",),
        "_create_backups": ("generator",),
        "_get_backup_list": ("dict",),
        "_update_metadata": ("Metadata",),
        "_remove_backups": ("generator",),
        "_get_discard_list": ("dict", "int", "int"),
    }
