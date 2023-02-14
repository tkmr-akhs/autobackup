import pytest
import pytest_mock
import pytest_raises

from autobackup import cnf


def test_validate_app_cnf_IfValidThenRaiseNoException():
    # Arrange
    app_cnf = {
        "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": "a"}
    }

    # Act & Assert
    cnf.validate_app_cnf(app_cnf)


def test_validate_app_cnf_IfDstDirpathIsEmptyStrThenRaiseNoException():
    # Arrange
    app_cnf = {
        "common": {"destination_dir": "", "tmp_dirpath": "a", "var_dirpath": "a"}
    }

    # Act
    with pytest.raises(cnf.CnfError) as cnf_error:
        cnf.validate_app_cnf(app_cnf)

    # Assert
    assert not cnf_error is None


def test_validate_app_cnf_IfTmpDirpathIsEmptyStrThenRaiseNoException():
    # Arrange
    app_cnf = {
        "common": {"destination_dir": "a", "tmp_dirpath": "", "var_dirpath": "a"}
    }

    # Act
    with pytest.raises(cnf.CnfError) as cnf_error:
        cnf.validate_app_cnf(app_cnf)

    # Assert
    assert not cnf_error is None


def test_validate_app_cnf_IfVarDirpathIsEmptyStrThenRaiseNoException():
    # Arrange
    app_cnf = {
        "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": ""}
    }

    # Act
    with pytest.raises(cnf.CnfError) as cnf_error:
        cnf.validate_app_cnf(app_cnf)

    # Assert
    assert not cnf_error is None


def test_validate_app_cnf_IfDistinationDirNameIsAbsolutePathThenRaiseNoException():
    # Arrange
    app_cnf = {
        "common": {"destination_dir": "/a", "tmp_dirpath": "a", "var_dirpath": "a"}
    }

    # Act
    with pytest.raises(cnf.CnfError) as cnf_error:
        cnf.validate_app_cnf(app_cnf)

    # Assert
    assert not cnf_error is None


def test_merge_cnf_CliCnfTakePrecedenceOverUsrCnf():
    # Arrange
    app_cnf = {}
    usr_cnf = {"common": {"destination_dir": "a", "tmp_dirpath": "a"}}
    cli_cnf = {"common": {"destination_dir": "b", "var_dirpath": "b"}}
    # Act
    cnf.merge_app_cnf(app_cnf, usr_cnf, cli_cnf)
    # Assert
    assert app_cnf == {
        "common": {"destination_dir": "b", "tmp_dirpath": "a", "var_dirpath": "b"}
    }


def test_merge_cnf_IfCliCnfIsNoneThenTakeNotPrecedenceOverUsrCnf():
    # Arrange
    app_cnf = {}
    usr_cnf = {"common": {"destination_dir": "a", "tmp_dirpath": "a"}}
    cli_cnf = {"common": {"destination_dir": None, "var_dirpath": "b"}}
    # Act
    cnf.merge_app_cnf(app_cnf, usr_cnf, cli_cnf)
    # Assert
    assert app_cnf == {
        "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": "b"}
    }


def test_merge_cnf_UsrCnfTakePrecedenceOverDefaultCnf():
    # Arrange
    app_cnf = {"common": {"destination_dir": "a", "tmp_dirpath": "a"}}
    usr_cnf = {"common": {"destination_dir": "b", "var_dirpath": "b"}}
    cli_cnf = {}
    # Act
    cnf.merge_app_cnf(app_cnf, usr_cnf, cli_cnf)
    # Assert
    assert app_cnf == {
        "common": {"destination_dir": "b", "tmp_dirpath": "a", "var_dirpath": "b"}
    }


def test_merge_cnf_CliCnfTakePrecedenceOverDefaultCnf():
    # Arrange
    app_cnf = {"common": {"destination_dir": "a", "tmp_dirpath": "a"}}
    usr_cnf = {}
    cli_cnf = {"common": {"destination_dir": "b", "var_dirpath": "b"}}
    # Act
    cnf.merge_app_cnf(app_cnf, usr_cnf, cli_cnf)
    # Assert
    assert app_cnf == {
        "common": {"destination_dir": "b", "tmp_dirpath": "a", "var_dirpath": "b"}
    }


def test_merge_cnf_IfCliCnfInNonThenNotTakePrecedenceOverDefaultCnf():
    # Arrange
    app_cnf = {"common": {"destination_dir": "a", "tmp_dirpath": "a"}}
    usr_cnf = {}
    cli_cnf = {"common": {"destination_dir": None, "var_dirpath": "b"}}
    # Act
    cnf.merge_app_cnf(app_cnf, usr_cnf, cli_cnf)
    # Assert
    assert app_cnf == {
        "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": "b"}
    }


def test_get_cli_cnf_IfCliArgsSetCnfThenReturnCnf():
    # Arrange
    args = [
        "progname",
        "--cnf_dirpath",
        "path/to/dir1",
        "--tmp_dirpath",
        "path/to/dir2",
        "--var_dirpath",
        "path/to/dir3",
        "--log_dirpath",
        "path/to/dir4",
        "--db_filename",
        "fileinfo.sqlite3",
        "--destination_dir",
        ".old",
        "--datetime_format",
        "_%Y-%m-%d",
        "--use_seq_num",
        "true",
        "--seq_num_sep",
        "_",
        "--discard_old_backup",
        "true",
        "--discard_phase1_weeks",
        "2",
        "--discard_phase2_months",
        "2",
        "--target",
        '{"path": "path/to/dir5", "catch_regex": ".*", "ignore_regex": "", "catch_hidden": true, "catch_link": false}',
        "--target",
        '{"path": "path/to/dir6", "catch_regex": ".*", "ignore_regex": "", "catch_hidden": true, "catch_link": false}',
    ]
    expected = {
        "common": {
            "cnf_dirpath": "path/to/dir1",
            "tmp_dirpath": "path/to/dir2",
            "var_dirpath": "path/to/dir3",
            "log_dirpath": "path/to/dir4",
            "db_filename": "fileinfo.sqlite3",
            "destination_dir": ".old",
            "datetime_format": "_%Y-%m-%d",
            "use_seq_num": True,
            "seq_num_sep": "_",
            "discard_old_backup": True,
            "discard_phase1_weeks": 2,
            "discard_phase2_months": 2,
        },
        "targets": [
            {
                "path": "path/to/dir5",
                "catch_regex": ".*",
                "ignore_regex": "",
                "catch_hidden": True,
                "catch_link": False,
            },
            {
                "path": "path/to/dir6",
                "catch_regex": ".*",
                "ignore_regex": "",
                "catch_hidden": True,
                "catch_link": False,
            },
        ],
    }

    # Act
    actual = cnf.get_cli_cnf(args)

    # Assert
    assert actual == expected


def test_get_cli_cnf_IfCliArgsSetNoneThenReturnCnfDictThatValueIsNone():
    # Arrange
    args = ["progname"]
    expected = {
        "common": {
            "cnf_dirpath": None,
            "tmp_dirpath": None,
            "var_dirpath": None,
            "log_dirpath": None,
            "db_filename": None,
            "destination_dir": None,
            "datetime_format": None,
            "use_seq_num": None,
            "seq_num_sep": None,
            "discard_old_backup": None,
            "discard_phase1_weeks": None,
            "discard_phase2_months": None,
        },
    }
    # Act
    actual = cnf.get_cli_cnf(args)

    # Assert
    assert actual == expected


def test_ConfigurationLoader_get_log_cnf_ReturnExpectedCnf():
    # Arrange
    cnf_loader = cnf.ConfigurationLoader("tests/data/cnf")

    # Act
    actual = cnf_loader.get_log_cnf({"common": {"log_dirpath": ""}}).keys()

    # Assert
    assert set(actual) == set(["version", "loggers", "handlers", "formatters"])


def test_Configuration_get_app_cnf_ReturnExpectedCnf():
    # Arrange
    cnf_loader = cnf.ConfigurationLoader("tests/data/cnf")

    # Act
    actual = cnf_loader.get_app_cnf({"common": {"cli_cnf_test": "Test"}})

    # Assert
    assert set(actual["common"].keys()) == set(
        [
            "tmp_dirpath",
            "var_dirpath",
            "log_dirpath",
            "db_filename",
            "destination_dir",
            "datetime_format",
            "use_seq_num",
            "seq_num_sep",
            "cli_cnf_test",
            "discard_old_backup",
            "discard_phase1_weeks",
            "discard_phase2_months",
        ]
    )
    assert set(actual["targets"][0].keys()) == set(
        ["ignore_regex", "path", "catch_hidden", "catch_link", "catch_regex"]
    )


def test_Configuration_get_app_cnf_IfInitWithNoneThenReturnExpectedCnf():
    # Arrange & Act
    cnf_loader = cnf.ConfigurationLoader("tests/data/cnf", None, None, None, None)
    actual = cnf_loader.get_app_cnf({"common": {"cli_cnf_test": "Test"}})

    # Assert
    assert set(actual["common"].keys()) == set(
        [
            "tmp_dirpath",
            "var_dirpath",
            "log_dirpath",
            "db_filename",
            "destination_dir",
            "datetime_format",
            "use_seq_num",
            "seq_num_sep",
            "cli_cnf_test",
            "discard_old_backup",
            "discard_phase1_weeks",
            "discard_phase2_months",
        ]
    )
    assert set(actual["targets"][0].keys()) == set(
        ["ignore_regex", "path", "catch_hidden", "catch_link", "catch_regex"]
    )
