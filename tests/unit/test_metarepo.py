import pytest
import pytest_mock
import pytest_raises
import sqlite3
from logging import DEBUG, ERROR, INFO, WARNING

from autobackup import metarepo


def test_MetadataRepository_get_current_metadatas_ReturnCurrentRecordsInDB():
    # Arrange
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
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

    # Act
    actual = [(item) for item in fidb.get_all_metadatas()]

    # Assert
    assert set(actual) == set(
        [
            metarepo.Metadata("/path/to/file1.ext", 0.0),
            metarepo.Metadata("/path/to/file2.ext", 0.0),
        ]
    )


def test_MetadataRepository_get_metadata_IfContainedThenReturnMetadata():
    # Arrange
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
    cur = dbconn.cursor()
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('/path/to/file1.ext',0.0)"
    )
    dbconn.commit()

    # Act
    actual = fidb.get_metadata("/path/to/file1.ext")

    # Assert
    assert actual == metarepo.Metadata("/path/to/file1.ext", 0.0)


def test_MetadataRepository_get_metadata_IfNotContainedThenReturnNone():
    # Arrange
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
    cur = dbconn.cursor()
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('/path/to/file1.ext',0.0)"
    )
    dbconn.commit()

    # Act
    actual = fidb.get_metadata("/path/to/file2.ext")

    # Assert
    assert actual == None


def test_MetadataRepository_get_inexistent_metadatas_ReturnRecordsToBeRemoved():
    # Arrange
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
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

    # Act
    actual = [(item) for item in fidb.get_uncontained_keys(new_info.keys())]

    # Assert
    assert set(actual) == set(["/path/to/file2.ext"])


def test_MetadataRepository_remove_metadatas_RemoveRecords(caplog):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.metarepo", INFO, "DELETE_FROM_DB: "),
        ("autobackup.metarepo", INFO, "DELETE_FROM_DB: "),
    ]
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
    cur = dbconn.cursor()
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('/path/to/file1.ext',0.0)"
    )
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('/path/to/file2.ext',0.0)"
    )
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('/path/to/file3.ext',0.0)"
    )
    dbconn.commit()

    remove_list = {"/path/to/file1.ext": None, "/path/to/file3.ext": None}

    # Act
    actual1 = [item for item in fidb.remove_metadatas(remove_list)]

    cur = dbconn.cursor()
    cur.execute(
        "SELECT "
        + metarepo._PATH_COL_NAME
        + ","
        + metarepo._MTIME_COL_NAME
        + " FROM "
        + metarepo._TABLE_NAME
    )

    actual2 = [item for item, _ in cur]
    actual3 = caplog.record_tuples

    # Assert
    assert set(actual1) == set(
        [
            metarepo.Metadata(key="/path/to/file1.ext", mtime=0.0),
            metarepo.Metadata(key="/path/to/file3.ext", mtime=0.0),
        ]
    )
    assert set(actual2) == set(["/path/to/file2.ext"])
    assert len(actual3) == len(expected_logs)
    for (
        (actual_module, actual_level, actual_message),
        (expected_module, expected_level, expected_message),
    ) in zip(actual3, expected_logs):
        assert actual_module == expected_module
        assert actual_level == expected_level
        assert actual_message.startswith(expected_message)


def test_MetadataRepository_pdate_metadata_UpdateRecord(
    mocker, caplog, FoundFileMock, build_path
):
    # Arrange
    caplog.set_level(DEBUG)
    expected_logs = [
        ("autobackup.metarepo", INFO, "REPLACE_INTO_DB: "),
    ]
    mocker.patch("autobackup.fsutil.FoundFile", new=FoundFileMock)
    dbconn = sqlite3.connect(":memory:")
    fidb = metarepo.MetadataRepository(dbconn)
    cur = dbconn.cursor()
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('{build_path('/path/to', file='file1.ext')}',0.0)"
    )
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('{build_path('/path/to', file='file2.ext')}',0.0)"
    )
    cur.execute(
        f"INSERT INTO {metarepo._TABLE_NAME}({metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME})\
            VALUES ('{build_path('/path/to', file='file3.ext')}',0.0)"
    )
    dbconn.commit()
    mdata = metarepo.Metadata(build_path("/path/to", file="file2.ext"), 1.0)

    # Act
    fidb.update_metadata(mdata)

    cur = dbconn.cursor()
    cur.execute(
        f"SELECT {metarepo._PATH_COL_NAME},{metarepo._MTIME_COL_NAME} FROM {metarepo._TABLE_NAME}"
    )

    actual1 = [(path, mtime) for path, mtime in cur]
    actual2 = caplog.record_tuples

    # Assert
    assert set(actual1) == set(
        [
            (build_path("/path/to", file="file1.ext"), 0.0),
            (build_path("/path/to", file="file2.ext"), 1.0),
            (build_path("/path/to", file="file3.ext"), 0.0),
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
