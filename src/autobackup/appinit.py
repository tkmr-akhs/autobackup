"""Module of initializing application"""
import pathlib


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
