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
        scanner.AllFileScanner([target_root], False),
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


def test_DestinationRepository_remove_backups_DiscardBackup(
    caplog, testdata_fresh, testdata_timestamp, rscan, build_path
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.dstrepo", WARNING, "DELETE_FILE: "),
        ("autobackup.dstrepo", WARNING, "DELETE_FILE: "),
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
