import pytest
import pytest_mock
import pytest_raises
import datetime
from logging import DEBUG, ERROR, INFO, WARNING
from os import sep


from autobackup import dstrepo, fsutil, scanner
from tests.testutil import testpath


def test_DestinationRepository_get_dst_file_ReturnDestinationFile(
    testdata, testdata_timestamp, mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11, False)


def test_DestinationRepository_get_dst_file_ReturnDestinationFile2(
    testdata, testdata_timestamp, mocker, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path_noseq(
        target_root, norm_path=False
    )
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", None)

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11, False)


def test_DestinationRepository_get_dst_file_IfSameMtimeThenReturnSkip(
    mocker, testdata_fresh, testdata_timestamp, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_fresh(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11, True)


def test_DestinationRepository_get_dst_file_IfSameMtimeThenReturnSkip2(
    mocker, testdata_fresh_noseq, testdata_timestamp, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_fresh_noseq(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path_noseq(
        target_root, norm_path=False
    )
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", None)

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11, True)


def test_DestinationRepository_get_dst_file_IfDifferMtimeThenReturnNotSkip(
    mocker, testdata_stale, testdata_timestamp, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_stale(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_old_path = testpath.dst_testfile11_path(target_root, norm_path=False)

    dst_testfile11_new_path = build_path(
        target_root,
        "TestDir1",
        ".old",
        file=f"TestFile11{datetime.datetime.fromtimestamp(testdata_timestamp).strftime('_%Y-%m-%d')}_0001",
        norm_path=False,
    )
    dst_testfile11_new = fsutil.FoundFile(
        dst_testfile11_new_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11_new, False)


def test_DestinationRepository_get_dst_file_IfDifferMtimeThenReturnNotSkip2(
    mocker, testdata_stale_noseq, testdata_timestamp, FoundFileMock, build_path
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_stale_noseq(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path_noseq(
        target_root, norm_path=False
    )
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", None)

    # Act
    actual = d_repo.get_dst_file(src_testfile11)

    # Assert
    assert actual == (dst_testfile11, False)


def test_DestinationRepository_create_backup_CreateBackup(
    mocker, caplog, testdata, testdata_timestamp, FoundFileMock, build_path, rscan
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [("autobackup.dstrepo", INFO, "COPY_FILE_TO_[")]
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual1 = d_repo.create_backup(src_testfile11)
    actual2 = rscan(target_root)
    actual3 = caplog.record_tuples

    # Assert
    assert actual1 == (src_testfile11, dst_testfile11)
    assert set(actual2) == set(
        [
            "TestFile",
            "TestDir1" + sep + "TestFile11",
            "TestDir1" + sep + "TestFile12.ext",
            "TestDir1" + sep + ".old" + sep + "TestFile11_2023-01-23_0000",
            "TestDir2" + sep + "TestFile22",
            "TestDir2" + sep + ".TestFile21",
        ]
    )
    assert len(actual3) == len(expected_logs)
    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual3, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)


def test_DestinationRepository_create_backup_IfSkipThenLog(
    mocker, caplog, testdata_fresh, testdata_timestamp, rscan, FoundFileMock, build_path
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [("autobackup.dstrepo", INFO, "SKIP(Already): ")]
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_fresh(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual1 = d_repo.create_backup(src_testfile11)
    actual2 = caplog.record_tuples

    # Assert
    assert actual1 == (src_testfile11, dst_testfile11)
    assert len(actual2) == len(expected_logs)

    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual2, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)


def test_DestinationRepository_create_backups_CreateBackupMultiply(
    mocker, caplog, testdata, testdata_timestamp, FoundFileMock, build_path, rscan
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.dstrepo", INFO, "COPY_FILE_TO_["),
        ("autobackup.dstrepo", INFO, "COPY_FILE_TO_["),
    ]
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata(__name__)

    src_testfile11_path = testpath.src_testfile11_path(target_root, norm_path=False)
    src_testfile11 = fsutil.FoundFile(
        src_testfile11_path, target_root, testdata_timestamp
    )

    src_testfile12_path = testpath.src_testfile12_path(target_root, norm_path=False)
    src_testfile12 = fsutil.FoundFile(
        src_testfile12_path, target_root, testdata_timestamp
    )

    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path, target_root, testdata_timestamp
    )

    dst_testfile12_path = testpath.dst_testfile12_path(target_root, norm_path=False)
    dst_testfile12 = fsutil.FoundFile(
        dst_testfile12_path, target_root, testdata_timestamp
    )

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual1 = [item for item in d_repo.create_backups([src_testfile11, src_testfile12])]
    actual2 = rscan(target_root)
    actual3 = caplog.record_tuples

    # Assert
    assert set(actual1) == set(
        [(src_testfile11, dst_testfile11), (src_testfile12, dst_testfile12)]
    )
    assert set(actual2) == set(
        [
            "TestFile",
            "TestDir1" + sep + "TestFile11",
            "TestDir1" + sep + "TestFile12.ext",
            "TestDir1" + sep + ".old" + sep + "TestFile11_2023-01-23_0000",
            "TestDir1" + sep + ".old" + sep + "TestFile12_2023-01-23_0000.ext",
            "TestDir2" + sep + "TestFile22",
            "TestDir2" + sep + ".TestFile21",
        ]
    )
    assert len(actual3) == len(expected_logs)
    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual3, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)


def test_DestinationRepository_get_current_backups_GetCurrentBackups(
    mocker, testdata_fresh, testdata_timestamp, rscan, FoundFileMock, build_path
):
    # Arrange
    from os.path import normcase

    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)

    target_root = testdata_fresh(__name__)

    dst_testfile_basename = build_path(
        target_root,
        ".old",
        file="TestFile",
        norm_path=False,
    )
    dst_testfile_path = testpath.dst_testfile_path(target_root, norm_path=False)
    dst_testfile = fsutil.FoundFile(
        dst_testfile_path,
        target_root,
        testdata_timestamp,
    )

    dst_testfile11_basename = build_path(
        target_root,
        "TestDir1",
        ".old",
        file="TestFile11",
        norm_path=False,
    )
    dst_testfile11_path = testpath.dst_testfile11_path(target_root, norm_path=False)
    dst_testfile11 = fsutil.FoundFile(
        dst_testfile11_path,
        target_root,
        testdata_timestamp,
    )

    dst_testfile12_basename = build_path(
        target_root,
        "TestDir1",
        ".old",
        file="TestFile12.ext",
        norm_path=False,
    )
    dst_testfile12_path = testpath.dst_testfile12_path(target_root, norm_path=False)
    dst_testfile12 = fsutil.FoundFile(
        dst_testfile12_path,
        target_root,
        testdata_timestamp,
    )

    dst_testfile21_basename = build_path(
        target_root,
        "TestDir2",
        ".old",
        file=".TestFile21",
        norm_path=False,
    )
    dst_testfile21_path = testpath.dst_testfile21_path(target_root, norm_path=False)
    dst_testfile21 = fsutil.FoundFile(
        dst_testfile21_path,
        target_root,
        testdata_timestamp,
    )

    dst_testfile22_basename = build_path(
        target_root,
        "TestDir2",
        ".old",
        file="TestFile22",
        norm_path=False,
    )
    dst_testfile22_path = testpath.dst_testfile22_path(target_root, norm_path=False)
    dst_testfile22 = fsutil.FoundFile(
        dst_testfile22_path,
        target_root,
        testdata_timestamp,
    )

    d_repo = dstrepo.DestinationRepository(
        scanner.AllFileScanner([{"path": target_root, "catch_link": False}]),
        ".old",
        "_%Y-%m-%d",
        "_",
    )

    # Act
    actual = dict(d_repo.get_all_backups())

    # Assert
    assert set(actual) == set(
        {
            dst_testfile.normpath_str: (
                dst_testfile,
                normcase(dst_testfile_basename),
            ),
            dst_testfile11.normpath_str: (
                dst_testfile11,
                normcase(dst_testfile11_basename),
            ),
            dst_testfile12.normpath_str: (
                dst_testfile12,
                normcase(dst_testfile12_basename),
            ),
            dst_testfile21.normpath_str: (
                dst_testfile21,
                normcase(dst_testfile21_basename),
            ),
            dst_testfile22.normpath_str: (
                dst_testfile22,
                normcase(dst_testfile22_basename),
            ),
        }
    )


def test_DestinationRepository_get_discard_list_IfFileInfoIsEmptyThenReturnEmptyList():
    # Arrange
    today = datetime.date(2023, 1, 22)
    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")
    all_files = {}

    # Act
    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert actual == []


def test_DestinationRepository_get_discard_list_IfNotBackupedFileThenNotContainIt(
    mocker, FoundFileMock
):
    # Arrange
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    today = datetime.date(2023, 1, 22)
    path0 = "path_to_dir" + sep + "file_2000-01-01_0000.txt"
    path0_mtime = datetime.datetime(2000, 1, 1, 1, 0, 0, 0).timestamp()

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    all_files = {path0: fsutil.FoundFile(path0, None, path0_mtime)}
    # Act

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    # Assert
    assert actual == []


def test_DestinationRepository_get_discard_list_IfFileInfoIsPhase1ThenReturnDiscardList(
    mocker, FoundFileMock, build_path
):
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

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    assert set(actual) == set(expected)


def test_DestinationRepository_get_discard_list_IfFileInfoIsPhase1ThenReturnDiscardList_2(
    mocker, FoundFileMock, build_path
):
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

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    assert set(actual) == set(expected)


def test_DestinationRepository_get_discard_list_IfFileInfoIsPhase2ThenReturnDiscardList(
    mocker, FoundFileMock, build_path
):
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

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    assert set(actual) == set(expected)


def test_DestinationRepository_get_discard_list_IfFileInfoIsPhase2ThenReturnDiscardList_2(
    mocker, FoundFileMock, build_path
):
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

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    assert set(actual) == set(expected)


def test_DestinationRepository_get_discard_list_IfSeqNumFlagIsDisabledThenReturnDiscardList(
    mocker, FoundFileMock, build_path
):
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

    actual = [item for item in d_repo.get_discard_list(all_files, today, 2, 2)]

    assert set(actual) == set(expected)


def test_DestinationRepository_remove_backups_DiscardBackup(
    caplog, testdata_fresh, testdata_timestamp, rscan, build_path
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.dstrepo", WARNING, "DELETE_OLD_FILE: "),
        ("autobackup.dstrepo", WARNING, "DELETE_OLD_FILE: "),
    ]
    target_root = testdata_fresh(__name__)

    dst_testfile12_path = testpath.dst_testfile12_path(target_root)
    dst_testfile21_path = testpath.dst_testfile21_path(target_root)

    remove_list = [dst_testfile12_path, dst_testfile21_path]

    d_repo = dstrepo.DestinationRepository(None, ".old", "_%Y-%m-%d", "_")

    # Act
    actual1 = [item for item in d_repo.remove_backups(remove_list)]
    actual2 = [item for item in rscan(target_root)]
    actual3 = caplog.record_tuples

    # Assert
    # assert set(actual1) == set([dst_testfile12_path, dst_testfile21_path])
    assert set(actual2) == set(
        [
            "TestFile",
            ".old" + sep + "TestFile_2023-01-23_0000",
            "TestDir1" + sep + "TestFile11",
            "TestDir1" + sep + ".old" + sep + "TestFile11_2023-01-23_0000",
            "TestDir1" + sep + "TestFile12.ext",
            "TestDir2" + sep + ".TestFile21",
            "TestDir2" + sep + "TestFile22",
            "TestDir2" + sep + ".old" + sep + "TestFile22_2023-01-23_0000",
        ]
    )
    assert len(actual3) == len(expected_logs)
    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual3, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)
