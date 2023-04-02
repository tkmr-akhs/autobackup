import pytest
import pytest_mock
import pytest_raises

from autobackup import cnf


class Test_validate_app_cnf:
    @staticmethod
    def test_IfValidThenRaiseNoException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": "a"}
        }

        # Act & Assert
        cnf.validate_app_cnf(app_cnf)

    @staticmethod
    def test_IfDstDirpathIsEmptyStrThenRaiseException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "", "tmp_dirpath": "a", "var_dirpath": "a"}
        }

        # Act
        with pytest.raises(cnf.CnfError) as cnf_error:
            cnf.validate_app_cnf(app_cnf)

        # Assert
        assert not cnf_error is None

    @staticmethod
    def test_IfTmpDirpathIsEmptyStrThenRaiseException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "a", "tmp_dirpath": "", "var_dirpath": "a"}
        }

        # Act
        with pytest.raises(cnf.CnfError) as cnf_error:
            cnf.validate_app_cnf(app_cnf)

        # Assert
        assert not cnf_error is None

    @staticmethod
    def test_IfVarDirpathIsEmptyStrThenRaiseException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": ""}
        }

        # Act
        with pytest.raises(cnf.CnfError) as cnf_error:
            cnf.validate_app_cnf(app_cnf)

        # Assert
        assert not cnf_error is None

    @staticmethod
    def test_IfDistinationDirNameIsAbsolutePathThenRaiseException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "/a", "tmp_dirpath": "a", "var_dirpath": "a"}
        }

        # Act
        with pytest.raises(cnf.CnfError) as cnf_error:
            cnf.validate_app_cnf(app_cnf)

        # Assert
        assert not cnf_error is None

    @staticmethod
    def test_IfTargetDirPathIsDuplicateThenRaiseException():
        # Arrange
        app_cnf = {
            "common": {"destination_dir": "a", "tmp_dirpath": "a", "var_dirpath": "a"},
            "targets": [{"path": "path1"}, {"path": "path1"}],
        }

        # Act
        with pytest.raises(cnf.CnfError) as cnf_error:
            cnf.validate_app_cnf(app_cnf)

        # Assert
        assert not cnf_error is None


class Test_merge_app_cnf:
    @staticmethod
    def test_CliCnfTakePrecedenceOverUsrCnf():
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

    @staticmethod
    def test_IfCliCnfIsNoneThenTakeNotPrecedenceOverUsrCnf():
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

    @staticmethod
    def test_UsrCnfTakePrecedenceOverDefaultCnf():
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

    @staticmethod
    def test_CliCnfTakePrecedenceOverDefaultCnf():
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

    @staticmethod
    def test_IfCliCnfInNonThenNotTakePrecedenceOverDefaultCnf():
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


class Test_get_cli_cnf:
    @staticmethod
    def test_IfCliArgsSetCnfThenReturnCnf():
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
            "--scan_symlink_dir",
            "false",
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
                "dry_run": False,
                "debug": False,
                "cnf_dirpath": "path/to/dir1",
                "tmp_dirpath": "path/to/dir2",
                "var_dirpath": "path/to/dir3",
                "log_dirpath": "path/to/dir4",
                "db_filename": "fileinfo.sqlite3",
                "destination_dir": ".old",
                "datetime_format": "_%Y-%m-%d",
                "use_seq_num": True,
                "seq_num_sep": "_",
                "scan_symlink_dir": True,
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

    @staticmethod
    def test_IfCliArgsSetNoneThenReturnCnfDictThatValueIsNone():
        # Arrange
        args = ["progname"]
        expected = {
            "common": {
                "dry_run": False,
                "debug": False,
                "cnf_dirpath": None,
                "tmp_dirpath": None,
                "var_dirpath": None,
                "log_dirpath": None,
                "db_filename": None,
                "destination_dir": None,
                "datetime_format": None,
                "use_seq_num": None,
                "seq_num_sep": None,
                "scan_symlink_dir": None,
                "discard_old_backup": None,
                "discard_phase1_weeks": None,
                "discard_phase2_months": None,
            },
        }
        # Act
        actual = cnf.get_cli_cnf(args)

        # Assert
        assert actual == expected


class Test_ConfigurationLoader_get_log_cnf:
    @staticmethod
    def test_ReturnExpectedCnf():
        # Arrange
        cnf_loader = cnf.ConfigurationLoader("tests/data/cnf")

        # Act
        actual = cnf_loader.get_log_cnf(
            {"common": {"log_dirpath": "", "debug": False}}
        ).keys()

        # Assert
        assert set(actual) == set(
            ["version", "loggers", "handlers", "filters", "formatters"]
        )


class Test_ConfigurationLoader_get_app_cnf:
    @staticmethod
    def test_ReturnExpectedCnf():
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
                "scan_symlink_dir",
                "discard_old_backup",
                "discard_phase1_weeks",
                "discard_phase2_months",
            ]
        )
        assert set(actual["targets"][0].keys()) == set(
            [
                "ignore_regex",
                "path",
                "catch_hidden",
                "catch_link",
                "catch_regex",
                "recursive",
            ]
        )

    @staticmethod
    def test_IfInitWithNoneThenReturnExpectedCnf():
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
                "scan_symlink_dir",
                "discard_old_backup",
                "discard_phase1_weeks",
                "discard_phase2_months",
            ]
        )
        assert set(actual["targets"][0].keys()) == set(
            [
                "ignore_regex",
                "path",
                "catch_hidden",
                "catch_link",
                "catch_regex",
                "recursive",
            ]
        )
