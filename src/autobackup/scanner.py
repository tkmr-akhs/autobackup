"""Module for AllFileScanner"""
from logging import getLogger

from . import fsutil


class AllFileScanner:
    """Get files in directories"""

    def __init__(
        self, target_dirs: dict[str, bool], scan_symlink_dir: bool, dst_dir_name: str
    ) -> None:
        """Initializer

        Args:
            targets (list[dict[str, Any]]): Scan target directories
        """
        self._logger = getLogger(__name__)
        self._target_dirs = target_dirs
        self._scan_symlink_dir = scan_symlink_dir
        self._dst_dir_name = dst_dir_name

    def get_all_files(self) -> dict[str, fsutil.FoundFile]:
        """Get files in directories.

        Returns:
            dict[str, fsutil.FoundFile]: Files that is found
        """
        result = {}
        files_total = 0
        dirs_total = 0
        r_scanner = fsutil.RecursiveScanDir()
        for target_path, recursive in self._target_dirs.items():
            if recursive:
                found_files_gen = r_scanner.recursive_scandir(
                    target_path, self._scan_symlink_dir
                )
            else:
                found_files_gen = r_scanner.scandir(target_path, self._dst_dir_name)

            found_files = [found_file for found_file in found_files_gen]

            for file in found_files:
                result[file.normpath_str] = file

            files_count = len(found_files)
            dirs_count = len({found_file.parent for found_file in found_files})
            files_total += files_count
            dirs_total += dirs_count
            self._logger.debug(
                "SCAN_DIR: (%i files, %i dirs) %s", files_count, dirs_count, target_path
            )

        self._logger.info("SCAN_DIR: total %i files, %i dirs", files_total, dirs_total)

        return result
