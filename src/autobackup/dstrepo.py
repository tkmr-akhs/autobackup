"""Module for backup destination repository"""
import datetime
import os
import pathlib
import re
import shutil
from collections.abc import Generator
from logging import getLogger

from .fsutil import FoundFile
from .scanner import AllFileScanner


#### Constants ####

_RE_SP = [".", "^", "$", "*", "+", "?", "{", "}", "[", "]", "\\", "|", "(", ")"]

_DTF_DICT = {
    "b": ".*",  # month name (short)
    "B": ".*",  # month name
    "y": "[0-9]{2}",  # year (00 -99)
    "Y": "[0-9]{4}",  # year
    "m": "[01][0-9]",  # month
    "d": "[0-3][0-9]",  # day
    "H": "[012][0-9]",  # hour (0 - 23)
    "I": "[01][0-9]",  # hour (1 - 12)
    "M": "[0-5][0-9]",  # minute
    "S": "[0-5][0-9]",  # second
    "f": "[0-9]{6}",  # microsecond
    "p": ".*",  # am/pm
    "z": "(|[+-][01][0-9][0-5][0-9]([0-5][0-9]|[0-5][0-9]\\.[0-9]{6}))",  # timezone offset
    "Z": ".*",  # timezone name
    "w": "[0-6]",  # weekday (0:sun - 6:sat)
    "a": "[0-6]",  # weekday name (0:sun - 6:sat) (short)
    "A": "[0-6]",  # weekday name (0:sun - 6:sat)
    "j": "[0-3][0-9][0-9]",  # days in year (000 - 366)
    "U": "[0-5][0-9]",  # weeks in year (sun is 1st) (00 - 53)
    "W": "[0-5][0-9]",  # weeks in year (mon is 1st) (00 - 53)
    "c": ".*",
    "x": ".*",
    "X": ".*",
    "%": "%",
}

#### Internal functions ####


def _convert_dtf_to_re(datetime_format: str) -> str:
    result = ""

    is_prev_percent = False
    for char in datetime_format:
        if is_prev_percent:
            result = result + _DTF_DICT[char]
            is_prev_percent = False
        elif char == "%":
            is_prev_percent = True
        else:
            if char in _RE_SP:
                result = result + "\\" + char
            else:
                result = result + os.path.normcase(char)

    return result


def _escape_re_sp(text: str) -> str:
    result = ""
    for char in text:
        if char in _RE_SP:
            result = result + "\\" + char
        else:
            result = result + char
    return result


#### Classes ####


class DestinationRepository:
    """Class for backup destination repository"""

    def __init__(
        self,
        scanner: AllFileScanner,
        dst_dir_name: str,
        datetime_format: str,
        seq_sep: str,
    ):
        """Initializer

        Args:
            scanner (AllFileScanner): AllFileScanner object
            dst_dir_name (str): Name of backup destination directory
            datetime_format (str): Date and time format to be appended to the backup file name
            seq_sep (str):\
                Separator between date and sequence number.\
                If None is passed, No sequence number will be assigned, and the backup\
                will be overwritten if the date/time string is the same.
        """
        self._scanner = scanner
        self._dst_dir_name = dst_dir_name
        self._datetime_format = datetime_format
        self._seq_sep = seq_sep
        self._check_filepath_re = self._get_check_filepath_re()
        self._logger = getLogger(__name__)

    def _build_dst_filepath(
        self,
        dir_path: pathlib.Path,
        file_name: str,
        mtime_date: str,
        seq_num: int,
        file_ext: str,
    ) -> str:
        # If this function is changed, _get_check_file_re() need to be also changed.
        if not self._seq_sep is None:
            result = os.path.join(
                str(dir_path),
                file_name
                + mtime_date
                + self._seq_sep
                + str(seq_num).zfill(4)
                + file_ext,
            )
        else:
            result = os.path.join(str(dir_path), file_name + mtime_date + file_ext)

        return result

    def _get_check_filepath_re(self) -> re.Pattern:
        # If this function is changed, _build_dst_filepath() need to be also changed.
        if not self._seq_sep is None:
            result = (
                "(.*"
                + _escape_re_sp(os.sep + os.path.normcase(self._dst_dir_name) + os.sep)
                + ".+)"
                + _convert_dtf_to_re(self._datetime_format)
                + _escape_re_sp(os.path.normcase(self._seq_sep))
                + "[0-9]{4}"
                + "(\\.[^.].*|)"
            )
        else:
            result = (
                "(.*"
                + _escape_re_sp(os.sep + os.path.normcase(self._dst_dir_name) + os.sep)
                + ".+)"
                + _convert_dtf_to_re(self._datetime_format)
                + "(\\.[^.].*|)"
            )

        return re.compile(result)

    def get_dst_file(
        self, src_file: FoundFile, all_files: dict[str, FoundFile] = None
    ) -> tuple[FoundFile, bool]:
        """Get the file from which the backup will be taken.

        Args:
            src_file (FoundFile): File of backup source

        Returns:
            tuple[FoundFile, bool]:\
                File of backup destination.\
                bool value indicates that a backup has already been created and may be skipped.
        """
        # Prepare each element composing the path.
        dir_path = src_file.parent
        dst_path = str(dir_path.joinpath(self._dst_dir_name))
        file_name = src_file.stem
        file_ext = src_file.suffix
        mtime_date = datetime.datetime.fromtimestamp(src_file.mtime).strftime(
            self._datetime_format
        )

        if self._seq_sep is None:
            return self._get_dst_path_without_seq(
                src_file, dst_path, file_name, mtime_date, file_ext, all_files
            )
        else:
            return self._get_dst_path_with_seq(
                src_file, dst_path, file_name, mtime_date, file_ext, all_files
            )

    def _get_dst_path_without_seq(
        self,
        src_file: FoundFile,
        dst_path: str,
        file_name: str,
        mtime_date: str,
        file_ext: str,
        all_files: dict[str, FoundFile],
    ):
        # Assemble the destination path from each element.
        dst_file = FoundFile(
            self._build_dst_filepath(dst_path, file_name, mtime_date, None, file_ext),
            str(src_file.scan_root_path),
        )

        is_skip = False

        if self._is_exist_file(dst_file, all_files):
            if dst_file.mtime == src_file.mtime:
                # Ignore if a backup has already been taken.
                is_skip = True

        return (dst_file, is_skip)

    def _get_dst_path_with_seq(
        self,
        src_file: FoundFile,
        dst_path: str,
        file_name: str,
        mtime_date: str,
        file_ext: str,
        all_files: dict[str, FoundFile],
    ):
        # Assemble the destination path from each element.
        seq_num = 0
        dst_filepath = self._build_dst_filepath(
            dst_path, file_name, mtime_date, seq_num, file_ext
        )

        is_skip = False

        while self._is_exist_file(dst_filepath, all_files):
            dst_file = self._build_dst_file(src_file, dst_filepath, all_files)
            if dst_file.mtime == src_file.mtime:
                # Ignore if a backup has already been taken.
                is_skip = True
                break

            seq_num += 1
            dst_filepath = self._build_dst_filepath(
                dst_path, file_name, mtime_date, seq_num, file_ext
            )
        else:
            dst_file = FoundFile(dst_filepath, src_file.scan_root_path)

        return (dst_file, is_skip)

    def _is_exist_file(self, filepath: str, all_files: dict[str, FoundFile]) -> bool:
        if all_files is None:
            return os.path.exists(filepath)
        else:
            return os.path.normcase(os.path.abspath(filepath)) in all_files.keys()

    def _build_dst_file(
        self, src_file: FoundFile, dst_filepath: str, all_files: dict[str, FoundFile]
    ) -> FoundFile:
        if all_files is None:
            return FoundFile(dst_filepath, src_file.scan_root_path)
        else:
            return all_files[os.path.normcase(os.path.abspath(dst_filepath))]

    def create_backup(self, src_file: FoundFile) -> tuple[FoundFile, FoundFile]:
        """Create a duplicate file for backup purposes.

        Args:
            src_file (FoundFile): Source files that need to be backed up.

        Returns:
            tuple[FoundFile, FoundFile]:\
                A file that have completed the backup process.\
                The previous value in the tuple is the source file, and the latter is\
                the destination file.
        """
        dst_file, is_skip = self.get_dst_file(src_file)
        dst_dir = dst_file.parent
        if is_skip:
            self._logger.info("SKIP(Already): %s", src_file)
            return (src_file, dst_file)
        else:
            try:
                if not dst_dir.exists():
                    dst_dir.mkdir()
                shutil.copy2(str(src_file), str(dst_file))
            except OSError as os_error:
                self._logger.warning("ERROR: %s", str(os_error))
                return None
            else:
                self._logger.info("COPY_FILE_TO_[%s]: %s", self._dst_dir_name, src_file)
                return (src_file, dst_file)

    def create_backups(
        self, src_list: list[FoundFile]
    ) -> Generator[tuple[FoundFile, FoundFile]]:
        """Create a duplicate files for backup purposes.

        Args:
            src_list (list[FoundFile]): List of source files that need to be backed up.

        Yields:
            tuple[FoundFile, FoundFile]: File that have completed the backup process
    
        Note:
            This method returns a Generator and processes one file at a time. To\
            complete the processing, all values must be retrieved from the Generator.
        """

        for src_file in src_list:
            result = self.create_backup(src_file)
            if not result is None:
                yield result

    def get_all_backups(
        self, all_files: dict[str, FoundFile] = None
    ) -> Generator[tuple[str, tuple[FoundFile, str]]]:
        """Get all backups.

        Args:
            all_files (dict[str, FoundFile], optional):\
                dict of information for all files already retrieved externally with AllFileScanner.\
                If omitted or None is passed, AllFileScanner is used internally.

        Yields:
            tuple[str, tuple[FoundFile, str]]:\
                dict of information about the current backup file. 
        """
        if all_files is None:
            all_files = self._scanner.get_all_files()

        for key, file in all_files.items():
            match_result = self._check_filepath_re.fullmatch(file.normpath_str)
            if not match_result is None:
                yield (key, (file, match_result.group(1) + match_result.group(2)))

    def remove_backup(self, file: FoundFile) -> FoundFile:
        """Remove the specified backup file.

        Args:
            file (FoundFile): File to be removed

        Returns:
            FoundFile: File that have completed the remove process

        """
        try:
            os.remove(str(file))
        except OSError as os_error:
            self._logger.warning("ERROR: %s", str(os_error))
            return None
        else:
            self._logger.warning("DELETE_FILE: %s", str(file))
            return file

    def remove_backups(self, files: list[FoundFile]) -> Generator[FoundFile]:
        """Remove the specified backup files.

        Args:
            files (list[FoundFile]): List of files to be removed

        Yields:
            FoundFile: File that have completed the remove process
    
        Note:
            This method returns a Generator and processes one file at a time. To\
            complete the processing, all values must be retrieved from the Generator.
        """
        for file in files:
            result = self.remove_backup(file)
            if not result is None:
                yield result
