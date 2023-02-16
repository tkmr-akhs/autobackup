"""Module for AllFileScanner"""
from typing import Any

from . import fsutil


class AllFileScanner:
    """Get files in directories"""

    def __init__(self, target_dirs: list[str], scan_symlink_dir: bool) -> None:
        """Initializer

        Args:
            targets (list[dict[str, Any]]): Scan target directories
        """
        self._target_dirs = target_dirs
        self._scan_symlink_dir = scan_symlink_dir

    def get_all_files(self) -> dict[str, fsutil.FoundFile]:
        """Get files in directories.

        Returns:
            dict[str, fsutil.FoundFile]: Files that is found
        """
        result = {}
        r_scanner = fsutil.RecursiveScanDir()
        for target_path in self._target_dirs:
            found_files = r_scanner.recursive_scandir(
                target_path, self._scan_symlink_dir
            )
            for file in found_files:
                result[file.normpath_str] = file

        return result
