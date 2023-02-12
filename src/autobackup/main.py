"""Module of main"""
import logging.config
import os
import sqlite3
from contextlib import closing
from logging import Logger, FileHandler, error, getLogger
import time

from .appinit import init_app
from .bkup import BackupFacade
from .cnf import CnfError, ConfigurationLoader, get_cli_cnf
from .repoinit import BackupRepositoryFactory, MetadataRepositoryFactory


class Main:
    """Class for entry point"""

    def __init__(self, args: list[str]) -> None:
        """Initializer

        Args:
            args (list[str]): Commandline arguments

        Raises:
            cnf_error: Rise when there is a problem with the config.
        """
        # Parsing command line arguments
        cli_cnf = get_cli_cnf(args)

        # Preparing ConfigurationLoader
        cnf_loader = ConfigurationLoader(cli_cnf["common"]["cnf_dirpath"])

        # Get App Configuration
        try:
            self._app_cnf = cnf_loader.get_app_cnf(cli_cnf)
        except CnfError as cnf_error:
            # At this point, logging is not yet configured, so logging to root's ERROR.
            error(str(cnf_error))
            raise cnf_error

        # Get Logging Configuration
        log_cnf = cnf_loader.get_log_cnf(self._app_cnf)

        #
        if self._app_cnf["common"]["use_seq_num"]:
            self._seq_num_sep = self._app_cnf["common"]["seq_num_sep"]
        else:
            self._seq_num_sep = None

        # Initialize app (e.g. Make tmp dir)
        init_app(self._app_cnf)

        # Configure Logging
        logging.config.dictConfig(log_cnf)
        self._logger = getLogger(__name__)

    def execute(self) -> int:
        """Main method.

        Returns:
            int: Exit code of command
        """
        exit_code = 0

        # Preparing the BackupRepositories
        b_factory = BackupRepositoryFactory(
            self._app_cnf["targets"],
            self._app_cnf["common"]["destination_dir"],
            self._app_cnf["common"]["datetime_format"],
            self._seq_num_sep,
        )
        s_repo = b_factory.get_source_repository()
        d_repo = b_factory.get_destination_repository()
        scnr = b_factory.get_all_file_scanner()

        with closing(
            sqlite3.connect(
                os.path.join(
                    self._app_cnf["common"]["var_dirpath"],
                    self._app_cnf["common"]["db_filename"],
                )
            )
        ) as dbconn:
            # Preparing the MetadatapRepository
            m_factory = MetadataRepositoryFactory(dbconn)
            m_repo = m_factory.get_metadata_repository()

            # Preparing the BackupFacade
            b_facade = BackupFacade(s_repo, d_repo, m_repo, scnr)

            # Execute
            b_facade.execute()

        self._logger.info("FINISH: autobackup")

        # for name in Logger.manager.loggerDict.keys():
        #     logger = getLogger(name)
        #     for handler in logger.handlers:
        #         if isinstance(handler, FileHandler):
        #             logger.removeHandler(handler)
        #             handler.close()
        # time.sleep(5)

        return exit_code
