"""Module of BackupFacade"""
import datetime
from collections.abc import Generator
from logging import getLogger

from . import dstrepo, metarepo, scanner, srcrepo
from .fsutil import FoundFile

_MTIME_ALLOW_ERR = 0.0000005


class BackupFacade:
    """It is a facade class that performs the steps involved in backing up a files."""

    def __init__(
        self,
        s_repo: srcrepo.SourceRepository,
        d_repo: dstrepo.DestinationRepository,
        m_repo: metarepo.MetadataRepository,
        scnr: scanner.AllFileScanner,
    ) -> None:
        """Initializer

        Args:
            s_repo (srcrepo.SourceRepository): SourceRepository object
            d_repo (dstrepo.DestinationRepository): DestinationRepository object
            m_repo (metarepo.MetadataRepository): MetadataRepository object
            scnr (scanner.AllFileScanner): AllFileScanner object
        """
        self._s_repo = s_repo
        self._d_repo = d_repo
        self._m_repo = m_repo
        self._scnr = scnr
        self._logger = getLogger(__name__)

    def execute(
        self,
        discard_old_backups: bool = True,
        phase1_weeks: int = 2,
        phase2_months: int = 2,
    ) -> None:
        """Execute backup."""
        # Get All Files
        all_files = self._scnr.get_all_files()

        # Get Source Files Generator
        src_files = dict(self._s_repo.get_files_matching_criteria(all_files))

        # Cleanup Metadata
        remove_list = self._m_repo.get_uncontained_keys(src_files.keys())
        for _ in self._m_repo.remove_metadatas(remove_list):
            pass

        # Create backups and Update Metadata
        backup_list = self._get_backup_list(src_files)
        processed_list = self._d_repo.create_backups(backup_list)
        for src_file, dst_file in processed_list:
            self._m_repo.update_metadata(
                metarepo.Metadata(src_file.normpath_str, src_file.mtime)
            )

        # Discard old backups
        if discard_old_backups:
            discard_list = self._d_repo.get_discard_list(
                all_files, phase1_weeks=phase1_weeks, phase2_months=phase2_months
            )
            for _ in self._d_repo.remove_backups(discard_list):
                pass

    def _get_backup_list(self, file_dict: dict[str, FoundFile]) -> Generator[FoundFile]:
        """Get a list of files that need to be backed up.

        Args:
            file_dict (dict[str, FoundFile]):\
                List of files to be checked for backup List of files that need to be backed up

        Yields:
            FoundFile: File that need to be backed up.
        """
        for key, file in file_dict.items():
            mdata = self._m_repo.get_metadata(key)

            if (
                mdata is None
                or mdata.mtime <= file.mtime - _MTIME_ALLOW_ERR
                or mdata.mtime > file.mtime + _MTIME_ALLOW_ERR
            ):
                yield file
