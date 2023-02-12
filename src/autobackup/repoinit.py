"""Module for initializing repositories."""
import sqlite3
from typing import Any

from .dstrepo import DestinationRepository
from .metarepo import MetadataRepository
from .scanner import AllFileScanner
from .srcrepo import SourceRepository


class MetadataRepositoryFactory:
    """Factoriy class of MetadataRepository"""

    def __init__(self, db_connection: sqlite3.Connection) -> None:
        """Initializer

        Args:
            db_connection (sqlite3.Connection): Connection to DB
        """
        self._dbconnection = db_connection

    def get_metadata_repository(self) -> MetadataRepository:
        """Get MetadataRepositry object.

        Returns:
            MetadataRepository: MetadataRepositry object
        """
        return MetadataRepository(self._dbconnection)


class BackupRepositoryFactory:
    """Factory class of SourceRepository and DestinationRepository"""

    def __init__(
        self,
        targets: list[dict[str, Any]],
        dst_dir_name: str,
        datetime_format: str,
        seq_num_sep: str = "_",
    ) -> None:
        """Initializer

        Args:
            targets (list[dict[str, Any]]):\
                dict of directory paths and search criterias to be backed up
            dst_dir_name (str): Name of backup destination directory
            datetime_format (str): Date and time format to be appended to the backup file name
            seq_num_sep (str, optional): \
                Separator between date and sequence number.\
                If None is passed, No sequence number will be assigned, and the backup\
                will be overwritten if the date/time string is the same.
        """
        self._targets = targets
        self._dst_dir_name = dst_dir_name
        self._datetime_format = datetime_format
        self._seq_num_sep = seq_num_sep
        self._scanner = AllFileScanner(targets)

    def get_source_repository(self) -> SourceRepository:
        """Get SourceRepository object.

        Returns:
            SourceRepository: SourceRepository object
        """
        return SourceRepository(self._scanner, self._targets, self._dst_dir_name)

    def get_destination_repository(self) -> DestinationRepository:
        """Get DestinationRepository object.

        Returns:
            DestinationRepository: DestinationRepository object
        """
        return DestinationRepository(
            self._scanner,
            self._dst_dir_name,
            self._datetime_format,
            self._seq_num_sep,
        )

    def get_all_file_scanner(self) -> AllFileScanner:
        """Get AllFileScanner object.

        Returns:
            AllFileScanner: AllFileScanner object
        """
        return self._scanner
