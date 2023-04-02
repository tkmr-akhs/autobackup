"""Module of initializing application"""
import datetime
import os
import pathlib
import shutil


def init_app(app_cnf: dict) -> None:
    """Initialize application.

    Args:
        app_cnf (dict): Application configuration
    """
    # Make Temporary Directory
    pathlib.Path(app_cnf["common"]["tmp_dirpath"]).mkdir(exist_ok=True)
    # Make Variable Directory
    pathlib.Path(app_cnf["common"]["var_dirpath"]).mkdir(exist_ok=True)
    # Make Log Directory
    pathlib.Path(app_cnf["common"]["log_dirpath"]).mkdir(exist_ok=True)

    # If the dry run option is enabled, back up the database files.
    if app_cnf["common"]["dry_run"]:
        db_file_path = os.path.join(
            app_cnf["common"]["var_dirpath"],
            app_cnf["common"]["db_filename"],
        )

        ts_suffix = datetime.datetime.fromtimestamp(
            os.stat(db_file_path).st_mtime
        ).strftime(".%Y-%m-%d_%H-%M-%S_%f")

        if os.path.exists(db_file_path):
            shutil.copy(db_file_path, db_file_path + ts_suffix)
