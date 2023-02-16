"""Module for backup source repository"""
import os
import re
from logging import getLogger
from typing import Any

from _collections_abc import Generator

from . import fsutil
from .scanner import AllFileScanner


def _get_target_dict(targets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for target in targets:
        key = os.path.normcase(os.path.abspath(target["path"]))
        result[key] = {
            "catch_regex": re.compile(target["catch_regex"]),
            "ignore_regex": re.compile(target["ignore_regex"]),
            "catch_hidden": target["catch_hidden"],
            "catch_link": target["catch_link"],
        }

    return result


class SourceRepository:
    """Class for backup source repository"""

    def __init__(
        self, scanner: AllFileScanner, targets: list[dict[str, Any]], dst_dir_name: str
    ) -> None:
        """Initializer

        Args:
            scanner (AllFileScanner): AllFileScanner object
            targets (list[dict[str, Any]]):\
                dict of directory paths and search criterias to be backed up
            dst_dir_name (str): Name of backup destination directory
        """
        self._scanner = scanner
        self._target_dict = _get_target_dict(targets)
        self._dst_dir_name = dst_dir_name
        self._logger = getLogger(__name__)

    def get_all_files(
        self, all_files: dict[str, fsutil.FoundFile] = None
    ) -> Generator[tuple[str, fsutil.FoundFile]]:
        """Get All files under the target path.

        Args:
            all_files (dict[str, fsutil.FoundFile], optional):\
                dict of information for all files already retrieved externally with AllFileScanner.\
                If omitted or None is passed, AllFileScanner is used internally.

        Yields:
            tuple[str, fsutil.FoundFile]: All files under the target path
        """
        if all_files is None:
            all_files = self._scanner.get_all_files()

        for key, file in all_files.items():
            if (
                os.sep + os.path.normcase(self._dst_dir_name) + os.sep
                in file.normpath_str
            ):
                self._logger.debug("NOT_SRC(BkupDir): %s", str(file))
                continue
            yield (key, file)

    def get_files_matching_criteria(
        self, all_files: dict[str, fsutil.FoundFile] = None
    ) -> Generator[tuple[str, fsutil.FoundFile]]:
        """Get files witch match search criteria under the target path.

        Args:
            all_files (dict[str, fsutil.FoundFile], optional):\
                dict of information for all files already retrieved externally with AllFileScanner.\
                If omitted or None is passed, AllFileScanner is used internally.

        Yields:
            tuple[str, fsutil.FoundFile]:
                The files witch match the search criteria. key is normalized path of\
                the file.
        """
        src_files = self.get_all_files(all_files)

        for key, file in src_files:
            target_dict_key = str(file.scan_root_path)

            target_criteria = self._target_dict[target_dict_key]

            if self._is_to_be_caught(
                file,
                target_criteria["catch_regex"],
                target_criteria["ignore_regex"],
                target_criteria["catch_hidden"],
                target_criteria["catch_link"],
            ):
                yield (key, file)

    def _is_to_be_caught(
        self,
        file: fsutil.FoundFile,
        catch_exp: re.Pattern,
        ignore_exp: re.Pattern,
        catch_hidden: bool,
        catch_link: bool,
    ) -> bool:
        if catch_hidden:
            if catch_link:
                return (
                    catch_exp.fullmatch(str(file.relpath)) is not None
                    and ignore_exp.fullmatch(str(file.relpath)) is None
                )
            else:
                return (
                    not self._is_symlink(file)
                    and catch_exp.fullmatch(str(file.relpath)) is not None
                    and ignore_exp.fullmatch(str(file.relpath)) is None
                )
        else:
            if catch_link:
                return (
                    not self._is_hidden(file)
                    and catch_exp.fullmatch(str(file.relpath)) is not None
                    and ignore_exp.fullmatch(str(file.relpath)) is None
                )
            else:
                return (
                    not self._is_hidden(file)
                    and not self._is_symlink(file)
                    and catch_exp.fullmatch(str(file.relpath)) is not None
                    and ignore_exp.fullmatch(str(file.relpath)) is None
                )

    def _is_hidden(self, file: fsutil.FoundFile):
        result = False

        try:
            result = file.is_hidden()
        except OSError as os_error:
            self._logger.debug("SKIP_HIDDEN_CHECK: %s: %s", str(file), str(os_error))

        return result

    def _is_symlink(self, file: fsutil.FoundFile):
        result = False

        try:
            result = file.is_symlink()
        except OSError as os_error:
            self._logger.debug("SKIP_SYMLINK_CHECK: %s: %s", str(file), str(os_error))

        return result
