"""Module for AllFileScanner"""
from typing import Any

from . import fsutil


class AllFileScanner:
    """Get files in directories"""

    def __init__(self, targets: list[dict[str, Any]]) -> None:
        """Initializer

        Args:
            targets (list[dict[str, Any]]): Scan target directories
        """
        self._targets = targets

    def get_all_files(self) -> dict[str, fsutil.FoundFile]:
        """Get files in directories.

        Returns:
            dict[str, fsutil.FoundFile]: Files that is found
        """
        result = {}
        r_scanner = fsutil.RecursiveScanDir()
        for target in self._targets:
            target_path = target["path"]
            catch_link = target["catch_link"]
            found_files = r_scanner.recursive_scandir(target_path, catch_link)
            for file in found_files:
                result[file.normpath_str] = file

        return result
