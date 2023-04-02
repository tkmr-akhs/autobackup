"""Module for configuration"""
import argparse
import json
import os
import pathlib
from logging import (
    NOTSET,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    Filter,
    LogRecord,
    getLevelName,
    getLevelNamesMapping,
)
from typing import Any

import tomllib

from . import dictutil

CNF_DIR = "cnf"
DEFAULT_CNF = "defaults.toml"
USR_CNF = "my_settings.toml"
LOG_CNF = "logging.toml"
LOG_NAME = "autobackup.log"


class CnfError(Exception):
    """Exception raised when there is a problem with the configuration."""


class ConfigurationLoader:
    """Class for loading configurations"""

    def __init__(
        self,
        cnf_dir: str = CNF_DIR,
        default_cnf: str = DEFAULT_CNF,
        usr_cnf: str = USR_CNF,
        log_cnf: str = LOG_CNF,
        log_name: str = LOG_NAME,
    ) -> None:
        """Initializer

        Args:
            cnf_dir (str, optional): Directory where config files are located. Defaults to CNF_DIR.
            default_cnf (str, optional): Default config file name. Defaults to DEFAULT_CNF.
            usr_cnf (str, optional):\
                Name of config file for user customization. Defaults to USR_CNF.
            log_cnf (str, optional): Logging config file name. Defaults to LOG_CNF.
        """
        if cnf_dir is None:
            cnf_dir = CNF_DIR
        if default_cnf is None:
            default_cnf = DEFAULT_CNF
        if usr_cnf is None:
            usr_cnf = USR_CNF
        if log_cnf is None:
            log_cnf = LOG_CNF
        if log_name is None:
            log_name = LOG_NAME

        self._cnf_dir = cnf_dir
        self._default_cnf = default_cnf
        self._usr_cnf = usr_cnf
        self._log_cnf = log_cnf
        self._log_name = log_name

    def get_app_cnf(self, cli_cnf: dict) -> dict:
        """Get app configuration.

        Args:
            cli_cnf: Configuration by command line arguments

        Returns:
            dict: App configuration

        Raises:
            CnfError: Config validation failed.
        """
        with open(os.path.join(self._cnf_dir, self._default_cnf), mode="rb") as fp:
            app_cnf = tomllib.load(fp)

        pathlib.Path(os.path.join(self._cnf_dir, self._usr_cnf)).touch(exist_ok=True)

        with open(os.path.join(self._cnf_dir, self._usr_cnf), mode="rb") as fp:
            usr_cnf = tomllib.load(fp)

        merge_app_cnf(app_cnf, usr_cnf, cli_cnf)

        validate_app_cnf(app_cnf)

        return app_cnf

    def get_log_cnf(self, app_cnf: dict[str, Any]) -> dict:
        """Get logging configuration.

        Returns:
            dict: Logging configuration
        """

        class _LevelOrHigherDiscardFilter(Filter):
            def __init__(self, level: str) -> None:
                super().__init__()
                self._level = getLevelNamesMapping().get(level, NOTSET)

            def filter(self, record: LogRecord) -> bool:
                return record.levelno < self._level

        with open(os.path.join(self._cnf_dir, self._log_cnf), mode="rb") as fp:
            log_cnf = tomllib.load(fp)

        log_cnf["handlers"]["fileHandler"]["filename"] = (
            os.path.normpath(app_cnf["common"]["log_dirpath"]) + os.sep + self._log_name
        )

        if app_cnf["common"]["debug"]:
            log_cnf["handlers"]["stdoutHandler"]["level"] = getLevelName(DEBUG)

        log_cnf["filters"]["levelOrHigherDiscardFilter"][
            "()"
        ] = _LevelOrHigherDiscardFilter

        return log_cnf


def validate_app_cnf(cnf: dict) -> None:
    """Validate app configuration.

    Args:
        cnf (dict): Configurations subject to validation

    Raises:
        CnfError: Raised when there is a problem with the configuration.
    """
    if cnf["common"]["destination_dir"] == "":
        raise CnfError("Configuration failed (destination_dir is empty)")

    if cnf["common"]["tmp_dirpath"] == "":
        raise CnfError("Configuration failed (tmp_dirpath is empty)")

    if cnf["common"]["var_dirpath"] == "":
        raise CnfError("Configuration failed (var_dirpath is empty)")

    if os.path.isabs(cnf["common"]["destination_dir"]):
        raise CnfError("Configuration failed (destination_dir is absolute path)")

    if "targets" in cnf and cnf["targets"]:
        target_paths = [target["path"] for target in cnf["targets"]]
        if len(target_paths) != len(set(target_paths)):
            raise CnfError("Duplicate target directory.")


def merge_app_cnf(
    app_cnf: dict[str, Any],
    usr_cnf: dict[str, Any],
    cli_cnf: dict[str, Any],
):
    """Merge app configuraions.

    Args:
        app_cnf (dict[str, ]): Application configuration
        usr_cnf (dict[str, ]): Configuration by file of user
        cli_cnf (dict[str, ]): Configuration from arguments of cli

    Note:
        This function has side effects and modifies the input dictionary "app_cfg".
    """
    dictutil.recursive_merge(app_cnf, usr_cnf)
    dictutil.recursive_merge(app_cnf, cli_cnf)


def get_cli_cnf(args: list[str]) -> dict[str, Any]:
    """Parses command line arguments into a dictionary.

    Args:
        args (list[str]): Command line arguments

    Returns:
        dict[str, Any]: Configuration from CLI
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Perform a dry run to preview changes without actually executing them."
        "The internal database is updated,"
        "but the database files are automatically backed up prior to execution.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print logs with the levels of INFO and DEBUG to the standard output.",
    )
    parser.add_argument(
        "--cnf_dirpath", help="Directory containing configuration files."
    )
    parser.add_argument("--tmp_dirpath", help="Directory to store temporary files.")
    parser.add_argument("--var_dirpath", help="Directory to store variable files.")
    parser.add_argument("--log_dirpath", help="Directory to log.")
    parser.add_argument("--db_filename", help="File name of DB used internally.")
    parser.add_argument(
        "--destination_dir",
        help="Name of the directory where the backup files will be stored. Must be a relative path.",
    )
    parser.add_argument(
        "--datetime_format", help="Format string of datetime (strftime format)"
    )
    parser.add_argument(
        "--use_seq_num",
        type=bool,
        help="Whether sequence number are used or not.",
    )
    parser.add_argument(
        "--seq_num_sep", help="Separator between file name and the sequence number."
    )
    parser.add_argument(
        "--target",
        action="append",
        help="Specify the target directory and matching criteria in JSON. <Example>: "
        '{"path": "path/to/dir", "catch_regex": ".*", "ignore_regex": "", "catch_hidden": true, "catch_link": false, "recursive": true}',
    )
    parser.add_argument(
        "--scan_symlink_dir",
        type=bool,
        help="Whether scan symbolic link directory or not.",
    )
    parser.add_argument(
        "--discard_old_backup",
        type=bool,
        help="Whether discard old backup or not.",
    )
    parser.add_argument(
        "--discard_phase1_weeks",
        type=int,
        help="The number of weeks that make up Phase 1, counting backwards from this week.",
    )
    parser.add_argument(
        "--discard_phase2_months",
        type=int,
        help="The number of months that make up Phase 2, counting backwards from this month.",
    )

    result_common = {}
    result_targets = []
    parsed_args = vars(parser.parse_args(args[1::]))

    for key, value in parsed_args.items():
        if key == "target":
            if not value is None:
                for target in value:
                    result_targets.append(json.loads(target))
        else:
            result_common[key] = value

    result = {}
    if len(result_common) > 0:
        result["common"] = result_common

    if len(result_targets) > 0:
        result["targets"] = result_targets

    return result
