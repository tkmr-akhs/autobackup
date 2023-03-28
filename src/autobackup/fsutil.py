"""Module of utilities related to file system"""
import os
import pathlib
import platform
import stat
from collections.abc import Generator
from logging import getLogger


class ScanLoopError(Exception):
    """Loop detected during recursive scan

    Exception raised when a loop is detected during a recursive scan that follows a\
    symbolic link.
    """


class RecursiveScanDir:
    """Class for scanning directry recursively"""

    def __init__(self) -> None:
        self._logger = getLogger(__name__)

    def _recursive_scandir(
        self, dirpath: str, scan_root: str, scan_symlink_dir: bool, found: list[str]
    ) -> Generator["FoundFile"]:
        for item in os.scandir(dirpath):
            item_hash = hash(os.path.normcase(os.path.realpath(item)))

            if item_hash in found:
                raise ScanLoopError(str(item))

            found.append(item_hash)

            if item.is_dir():
                if scan_symlink_dir or not item.is_symlink():
                    yield from self._recursive_scandir(
                        item.path, scan_root, scan_symlink_dir, found
                    )
            else:
                yield FoundFile(item.path, scan_root)

    def recursive_scandir(
        self, dirpath: str = ".", scan_symlink_dir: bool = True
    ) -> Generator["FoundFile"]:
        """Scan directory recursively.

        Args:
            dirpath (str, optional): Directory to scan recursively. Defaults to ".".
            catch_link (bool, optional):\
                Whether to scan the directory where the symbolic link leads. Defaults to True.

        Yields:
            FoundFile: FoundFile object pointing to the path of file.
        """
        yield from self._recursive_scandir(dirpath, dirpath, scan_symlink_dir, [])


class FoundFile(os.PathLike):
    """Class of file which scanned with recursice_scandir() method"""

    def __init__(self, filepath: str, scan_root_dirpath: str = None) -> None:
        """Initializer

        Args:
            filepath (str): Path string of the found file.
            scan_root_dirpath (str, optional):\
                Path string of the directory that acts as the starting point for\
                scanning files recursively.
        """
        filepath = os.path.abspath(filepath)
        self.path = pathlib.Path(filepath)

        if scan_root_dirpath is None:
            scan_root_dirpath = os.path.dirname(filepath)

        self.scan_root_path = pathlib.Path(
            os.path.normcase(os.path.abspath(scan_root_dirpath))
        )

    @property
    def relpath(self) -> pathlib.Path:
        """Relative path"""
        return self.path.relative_to(self.scan_root_path)

    @property
    def normpath_str(self) -> str:
        """Normalized path"""
        return os.path.normpath(os.path.normcase(str(self)))

    @property
    def size(self) -> int:
        """st_size of file"""
        return self.path.stat().st_size

    @property
    def mtime(self) -> float:
        """st_mtime of file"""
        return self.path.stat().st_mtime

    @property
    def name(self) -> str:
        """Name of file"""
        return self.path.name

    @property
    def stem(self) -> str:
        """Base name of file(stem)"""
        # if self.path.stem == "":
        #     return self.path.suffix
        # else:
        #     return self.path.stem
        return self.path.stem

    @property
    def suffix(self) -> str:
        """Suffix of file name (a.k.a file extention)"""
        # if self.path.stem == "":
        #     return ""
        # else:
        #     return self.path.suffix
        return self.path.suffix

    @property
    def parent(self) -> pathlib.Path:
        """Parent directry"""
        relpath = self.path.parent.relative_to(self.scan_root_path)
        return pathlib.Path(
            os.path.normpath(os.path.join(self.scan_root_path, relpath))
        )

    def __str__(self) -> str:
        return os.path.join(str(self.scan_root_path), str(self.relpath))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, FoundFile):
            return hash(self) == hash(__o)
        elif isinstance(__o, os.PathLike):
            return self.path == __o
        elif isinstance(__o, str):
            return str(self.path) == __o
        elif isinstance(__o, bytes):
            return bytes(self.path) == __o
        else:
            return NotImplemented

    def __hash__(self):
        return hash(str(self)) ^ hash(self.scan_root_path)

    def __fspath__(self):
        return str(self)

    def __bytes__(self):
        """Return the bytes representation of the path.  This is only
        recommended to use under Unix."""
        return os.fsencode(self)

    def samefile(self, __o):
        """Whether same file or not.

        Args:
            __o: Whether same file or not.
        """
        self.path.samefile(__o)

    def is_symlink(self) -> bool:
        """Whether this path is symbolic link or not.

        Returns:
            bool: Whether this path is symbolic link or not.
        """
        return self.path.is_symlink()

    def stat(self) -> os.stat_result:
        """Get status of file

        Returns:
            os.stat_result: Status of file
        """
        return self.path.stat()

    def exists(self) -> bool:
        """Whether this file exists of not.

        Returns:
            bool: Whether this file exists of not.
        """
        return self.path.exists()

    def is_hidden(self) -> bool:
        """Whether this file is hidden or not.

        Raises:
            RuntimeError: Raise this exception when failing to identify the operating system

        Returns:
            bool: Whether this file is hidden or not
        """
        pf = platform.system()

        if pf == "Windows":
            return self.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

        if pf == "Darwin":
            return (self.stat().st_flags & stat.UF_HIDDEN) or self.name.startswith(".")

        if pf == "Linux":
            return self.name.startswith(".")

        raise RuntimeError(f"unexpected platform name: {pf}")
