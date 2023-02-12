"""Module to update database based on dictionary of new file information"""
import sqlite3
from collections.abc import Generator
from logging import getLogger
from typing import NamedTuple

_TABLE_NAME = "fileinfo"
_PATH_COL_NAME = "path"
_MTIME_COL_NAME = "mtime"


def _esc_sp_ch(target: str) -> str:
    result = target.replace("'", "''")
    result = "'" + result + "'"
    return result


class Metadata(NamedTuple):
    """Class of Metadata"""

    key: str
    mtime: float


class MetadataRepository:
    """Class of repository for storing file metadata"""

    def __init__(self, db_connection: sqlite3.Connection):
        """Initializer

        Args:
            db_connection (sqlite3.Connection): Connection to DB
        """
        self._dbconn = db_connection
        self._logger = getLogger(__name__)

        cur = self._dbconn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {_TABLE_NAME}({_PATH_COL_NAME} TEXT PRIMARY KEY, {_MTIME_COL_NAME} REAL)"
        )
        self._dbconn.commit()
        cur.close()

    def get_metadata(self, key: str) -> Metadata:
        """Get metadata by key from this repository.

        Args:
            key (str): Normalized file path

        Returns:
            Metadata: Metadata. If key is not contain in repo then return None.
        """
        cur = self._dbconn.cursor()

        cur.execute(
            f"SELECT {_MTIME_COL_NAME} FROM {_TABLE_NAME} WHERE {_PATH_COL_NAME} = {_esc_sp_ch(key)}"
        )
        mtime = None
        for (tmp,) in cur:
            mtime = tmp

        cur.close()

        if mtime is None:
            return None
        else:
            return Metadata(key, mtime)

    def get_all_metadatas(self) -> Generator[Metadata]:
        """Get all metadata from this repository.

        Yields:
            Metadata: Metadata
        """
        cur = self._dbconn.cursor()
        for key, mtime in cur.execute(
            f"SELECT {_PATH_COL_NAME},{_MTIME_COL_NAME} FROM {_TABLE_NAME}"
        ):
            yield Metadata(key, mtime)
        cur.close()

    def get_uncontained_keys(self, keys: list[str]) -> Generator[str]:
        """Extracts keys that are present in this repository but not in the given list.

        Keys that are only contained in the given list will be ignored.

        Args:
            keys (list[str]): List of keys to compare against

        Yields:
            str: Key that are present in this repository but not in the given list
        """
        current_list = self.get_all_metadatas()
        for mdata in current_list:
            if not mdata.key in keys:
                yield mdata.key

    def remove_metadata(self, key: str, do_commit: bool = True) -> Metadata:
        """Remove the specified metadata from this repository.

        Args:
            key (str): Key of metadata to be removed.
            do_commit (bool, optional):\
                Whether the commit process is handled internally or not. Defaults to True.

        Returns:
            Metadata: Removed metadata
        """
        result = self.get_metadata(key)

        cur = self._dbconn.cursor()
        cur.execute(
            f"DELETE FROM {_TABLE_NAME} WHERE {_PATH_COL_NAME} = {_esc_sp_ch(key)}"
        )
        self._logger.info("DELETE_FROM_DB: %s", key)
        cur.close()
        if do_commit:
            self._dbconn.commit()

        return result

    def remove_metadatas(
        self, keys: list[str], do_commit: bool = True
    ) -> Generator[Metadata]:
        """Remove the specified metadatas from this repository.

        Args:
            keys (list[str]): List of Keys of metadata to be removed.
            do_commit (bool, optional):\
                Whether the commit process is handled internally or not. Defaults to True.

        Yields:
            Metadata: Removed metadata

        Note:
            This method returns a Generator and processes one file at a time. To\
            complete the processing, all values must be retrieved from the Generator.
        """
        for remove_item in keys:
            result = self.remove_metadata(remove_item, False)
            if not result is None:
                yield result
        if do_commit:
            self._dbconn.commit()

    def update_metadata(self, mdata: Metadata, do_commit: bool = True) -> None:
        """Update the metadatas in this repository.
        
        If the key does not exist in the repository, new metadata will be registered.

        Args:
            mdata (Metadata): Metadata to update or register new
            do_commit (bool, optional):\
                Whether the commit process is handled internally or not. Defaults to True.
        """
        cur = self._dbconn.cursor()

        cur.execute(
            f"REPLACE INTO {_TABLE_NAME}({_PATH_COL_NAME},{_MTIME_COL_NAME}) VALUES({_esc_sp_ch(mdata.key)},{str(mdata.mtime)})"
        )
        self._logger.info("REPLACE_INTO_DB: %s", mdata.key)

        cur.close()
        if do_commit:
            self._dbconn.commit()
