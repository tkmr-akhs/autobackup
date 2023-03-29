"""Module of BackupFacade"""
import datetime
import math
from collections.abc import Generator
from logging import getLogger
from typing import Any

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
        """Execute backup.

        Args:
            discard_old_backups (bool, optional):\
                Whether to discard old backups. Defaults to True.
            phase1_weeks (int, optional):
                The number of weeks that make up Phase 1, counting backwards from\
                this week. Defaults to 2.
            phase2_months (int, optional):
                The number of months that make up Phase 2, counting backwards from\
                this month. Defaults to 2.
        """
        # Get All Files
        all_files = self._scnr.get_all_files()

        # Get Source Files Generator
        src_files = dict(self._s_repo.get_files_matching_criteria(all_files))

        # Cleanup Metadata
        remove_list = self._get_uncontained_keys(src_files.keys())
        for _ in self._m_repo.remove_metadatas(remove_list):
            pass

        # Create backups and Update Metadata
        modified_files = self._get_modified_files(src_files)
        processed_files = self._d_repo.create_backups(modified_files)

        total_size = 0
        for src_file, dst_file in processed_files:
            total_size += src_file.size
            self._m_repo.update_metadata(
                metarepo.Metadata(src_file.normpath_str, src_file.mtime)
            )

        self._logger.info("TOTAL_SIZE: %i MB", math.ceil(total_size / 1024.0 / 1024.0))

        # Discard old backups
        if discard_old_backups:
            files_to_be_discarded = self._get_files_to_be_discarded(
                all_files, phase1_weeks=phase1_weeks, phase2_months=phase2_months
            )
            for _ in self._d_repo.remove_backups(files_to_be_discarded):
                pass
        else:
            pass

    def _get_uncontained_keys(self, keys: list[str]) -> Generator[str]:
        """Extracts keys that are present in MetadataRepository but not in the given list.

        Keys that are only contained in the given list will be ignored.

        Args:
            keys (list[str]): List of keys to compare against

        Yields:
            str: Key that are present in this repository but not in the given list
        """
        current_list = self._m_repo.get_all_metadatas()
        for mdata in current_list:
            if not mdata.key in keys:
                yield mdata.key

    def _get_modified_files(
        self, file_dict: dict[str, FoundFile]
    ) -> Generator[FoundFile]:
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

    def _get_files_to_be_discarded(
        self,
        all_files: dict[str, FoundFile] = None,
        today: datetime.date = datetime.date.today(),
        phase1_weeks: int = None,
        phase2_months: int = None,
    ) -> Generator[FoundFile]:
        """Get a list of files to be discarded.

        By default, files that are up to 2 weeks old are all kept and not listed as\
        files to be discarded.
        Files from 2 weeks to 2 months old are in Phase 1, and files older than 2\
        months are in Phase 2.

        In Phase 1, only the latest file per day is kept, the rest are discarded. In\
        Phase 2, only the latest file per week is kept, and the rest are discarded.

        Args:
            all_files (dict[str, FoundFile], optional):\
                dict of information for all files already retrieved externally with AllFileScanner.\
                If omitted or None is passed, AllFileScanner is used internally.
            today (datetime.date, optional):\
                The date that serves as the starting point for determining the actual\
                duration of Phase 1 or Phase 2. Defaults to datetime.date.today().
            phase1_weeks (int, optional):
                The number of weeks that make up Phase 1, counting backwards from\
                this week. Defaults to None.
            phase2_months (int, optional):
                The number of months that make up Phase 2, counting backwards from\
                this month. Defaults to None.

        Yields:
            FoundFile: A file to be discarded
        """
        dst_files = self._d_repo.get_all_backups(all_files)

        dst_files_dict = dict(dst_files)

        result = []
        if len(dst_files_dict) < 1:
            yield from result

        # Date of Phase Switchover
        phase1 = _get_phase1_date(today, phase1_weeks)
        phase2 = _get_phase2_date(today, phase2_months)

        # Temporary dict
        phase1_keep = {}
        phase2_keep = {}
        for key, (file, base_path) in dst_files_dict.items():
            mtime = datetime.datetime.fromtimestamp(file.mtime)

            if _is_in_phase2(mtime, phase1, phase2):
                # phase2: keep newest file per week
                aggregation_date = mtime.date() - datetime.timedelta(
                    days=mtime.date().weekday()
                )
                _separate_keep_and_discard_backup_files(
                    result,
                    phase2_keep,
                    mtime,
                    aggregation_date,
                    base_path,
                    file,
                )
            elif _is_in_phase1(mtime, phase1, phase2):
                # phase1: keep newest file per day
                aggregation_date = mtime.date()
                _separate_keep_and_discard_backup_files(
                    result,
                    phase1_keep,
                    mtime,
                    aggregation_date,
                    base_path,
                    file,
                )

        # It is not worth being yield at this time.
        # This is in case we come up with a way to make it more efficient in the future.
        yield from result


def _separate_keep_and_discard_backup_files(
    discard_list: list[FoundFile],
    keep_list: dict[datetime.datetime, dict[str, dict[str, Any]]],
    mtime: datetime.datetime,
    aggregation_date: datetime.datetime,
    file_base_path: str,
    file: FoundFile,
) -> None:
    """Classify backup files into those to be kept and discarded.

    Args:
        discard_list (list[FoundFile]): A list of files to be discarded.
        keep_list (dict[datetime.datetime, dict[str, dict[str, Any]]]):\
            A dictionary of files to be kept.
        mtime (datetime.datetime): The modification time of the file.
        aggregation_date (datetime.datetime): The date from which the aggregation starts.
        file_base_path (str):\
            The base path of a backed-up file excluding the date and sequence number.
        file (FoundFile): File to be classified

    Note:
        This function has side effects and modifies thie input list "discard_files" and the\
        dictionary "keep_files".
    """
    if aggregation_date in keep_list and file_base_path in keep_list[aggregation_date]:
        if keep_list[aggregation_date][file_base_path]["mtime"] < mtime:
            discard_list.append(keep_list[aggregation_date][file_base_path]["file"])
            keep_list[aggregation_date][file_base_path]["file"] = file
            keep_list[aggregation_date][file_base_path]["mtime"] = mtime
        else:
            discard_list.append(file)
    else:
        keep_list[aggregation_date] = {file_base_path: {"file": file, "mtime": mtime}}


def _get_phase1_date(today: datetime.date, phase1_weeks: int) -> datetime.date:
    if phase1_weeks is None:
        return None

    if phase1_weeks <= 0:
        return None

    return today - datetime.timedelta(
        days=today.weekday() + 7 * math.floor(phase1_weeks)
    )


def _get_phase2_date(today: datetime.date, phase2_months: int) -> datetime.date:
    if phase2_months is None:
        return None

    if phase2_months <= 0:
        return None

    p2_years = math.floor(phase2_months / 12)
    p2_months = math.floor(phase2_months - p2_years * 12)
    if today.month <= p2_months:
        # subtraction carry forward
        return datetime.date(today.year - p2_years - 1, today.month + 12 - p2_months, 1)
    else:
        return datetime.date(today.year - p2_years, today.month - p2_months, 1)


def _is_in_phase1(
    mtime: datetime.datetime, phase1: datetime.date, phase2: datetime.date
) -> bool:
    return not phase1 is None and mtime.date() < phase1


def _is_in_phase2(
    mtime: datetime.datetime, phase1: datetime.date, phase2: datetime.date
) -> bool:
    return not phase2 is None and mtime.date() < phase2 and mtime.date() < phase1
