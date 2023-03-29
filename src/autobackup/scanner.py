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
        prev_total = 0
        current_total = -1
        r_scanner = fsutil.RecursiveScanDir()
        for target_path, recursive in self._target_dirs.items():
            if recursive:
                found_files = r_scanner.recursive_scandir(
                    target_path, self._scan_symlink_dir
                )
            else:
                found_files = r_scanner.scandir(target_path, self._dst_dir_name)

            for file in found_files:
                result[file.normpath_str] = file

            current_total = len(result)
            self._logger.info(
                "SCAN_DIR: (%i files) %s", current_total - prev_total, target_path
            )
            prev_total = current_total

        return result
