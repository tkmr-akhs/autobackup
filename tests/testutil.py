import pytest
import pytest_mock
import pytest_raises
import datetime
import os
import pathlib

from autobackup.fsutil import FoundFile
from autobackup.scanner import AllFileScanner

TESTDATA_TIMESTAMP = datetime.datetime(2023, 1, 23, 4, 56, 12, 345678).timestamp()


class AllFileScannerMock(AllFileScanner):
    def __init__(
        self,
        targets=None,
        scan_symlink_dir: bool = False,
        dst_dir_name: str = ".old",
        all_files: dict[str, FoundFile] = {},
    ) -> None:
        super().__init__(targets, scan_symlink_dir, dst_dir_name)
        self._all_files = all_files

    def get_all_files(self) -> dict[str, FoundFile]:
        return self._all_files


class FoundFileMock(FoundFile):
    def __init__(
        self,
        filepath: str,
        scan_root_dirpath: str = None,
        mtime: float = 0.0,
        is_hidden_flag: bool = False,
        size: int = 4096,
    ) -> None:
        super().__init__(filepath, scan_root_dirpath)
        self._mtime = mtime
        self._size = size
        self._is_hidden_flag = is_hidden_flag

    @property
    def mtime(self) -> float:
        return self._mtime

    @property
    def size(self) -> int:
        return self._size

    def is_hidden(self) -> bool:
        import platform

        pf = platform.system()

        if pf == "Windows":
            return self._is_hidden_flag

        if pf == "Darwin":
            return self._is_hidden_flag or self.name.startswith(".")

        if pf == "Linux":
            return self.name.startswith(".")


def rscan(scan_root: str):
    scan_root_path = pathlib.Path(scan_root).absolute()
    for entry in scan_root_path.rglob("*"):
        if entry.is_file():
            yield str(entry.absolute().relative_to(scan_root_path))


def build_path(
    path: str,
    *dirs: str,
    file: str = None,
    abs_path: bool = True,
    norm_path: bool = True,
    norm_dir: bool = False,
    norm_file: bool = False,
):
    if path is None or path == "":
        result = ""
    else:
        if abs_path:
            path = os.path.abspath(path)

        if norm_path:
            result = os.path.normcase(path)
        else:
            result = path

    for dir in dirs:
        if not dir is None and dir != "":
            if norm_dir:
                result = os.path.join(result, os.path.normcase(dir))
            else:
                result = os.path.join(result, dir)

    if not file is None:
        if norm_file:
            result = os.path.join(result, os.path.normcase(file))
        else:
            result = os.path.join(result, file)

    return result


class testpath:
    # SOURCES

    # Source Directories
    @classmethod
    def src_testdir_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testdir1_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testdir2_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    # Source Files
    @classmethod
    def src_testfile_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            file="TestFile",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testfile11_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            file="TestFile11",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testfile12_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            file="TestFile12.ext",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testfile21_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            file=".TestFile21",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def src_testfile22_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            file="TestFile22",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    # DESTINATIONS

    # Destination Directories

    @classmethod
    def dst_testdir_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            ".old",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testdir1_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            ".old",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testdir2_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            ".old",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    # Destination Files

    @classmethod
    def dst_testfile_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            ".old",
            file=f"TestFile{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile11_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            ".old",
            file=f"TestFile11{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile12_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            ".old",
            file=f"TestFile12{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000.ext",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile21_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            ".old",
            file=f".TestFile21{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile22_path(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            ".old",
            file=f"TestFile22{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    # Destination Files (none sequence number)

    @classmethod
    def dst_testfile_path_noseq(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            ".old",
            file=f"TestFile{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}_0000",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile11_path_noseq(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            ".old",
            file=f"TestFile11{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile12_path_noseq(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir1",
            ".old",
            file=f"TestFile12{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}.ext",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile21_path_noseq(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            ".old",
            file=f".TestFile21{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )

    @classmethod
    def dst_testfile22_path_noseq(
        cls,
        target_dir: str,
        abs_path: bool = True,
        norm_path: bool = True,
        norm_dir: bool = False,
        norm_file: bool = False,
    ) -> str:
        return build_path(
            target_dir,
            "TestDir2",
            ".old",
            file=f"TestFile22{datetime.datetime.fromtimestamp(TESTDATA_TIMESTAMP).strftime('_%Y-%m-%d')}",
            abs_path=abs_path,
            norm_path=norm_path,
            norm_dir=norm_dir,
            norm_file=norm_file,
        )


class dummyfile:
    @classmethod
    def get_file(
        cls,
        path: str,
        *dirs: str,
        file_prefix: str = "TestFile",
        file_suffix: str = "",
        strftime: str = None,
        seq: int = 0,
        seq_num_sep: str = None,
        mtime: float = 0.0,
        is_hidden_flag: bool = False,
    ) -> FoundFile:
        if not seq_num_sep is None:
            seq_str = seq_num_sep + str(seq).zfill(4)
        else:
            seq_str = ""

        if not strftime is None:
            mtime_str = datetime.datetime.fromtimestamp(mtime).strftime(strftime)
        else:
            mtime_str = ""

        file = FoundFileMock(
            build_path(
                path,
                *dirs,
                file=f"{file_prefix}{mtime_str}{seq_str}{file_suffix}",
                norm_path=False,
            ),
            path,
            mtime,
            is_hidden_flag,
        )

        return file

    @classmethod
    def get_files(
        cls,
        mtime_date: datetime.date,
        path: str,
        *dirs: str,
        file_prefix: str = "TestFile",
        file_suffix: str = "",
        strftime: str = "_%Y-%m-%d",
        seq_num: int = 3,
        seq_num_sep: str = "_",
    ) -> dict[str, FoundFile]:
        result = {}

        for seq in range(0, seq_num):
            dst_file = cls.get_file(
                path,
                *dirs,
                file_prefix=file_prefix,
                file_suffix=file_suffix,
                strftime=strftime,
                seq=seq,
                seq_num_sep=seq_num_sep,
                mtime=(
                    datetime.datetime(
                        mtime_date.year, mtime_date.month, mtime_date.day, 0, 0, 0
                    )
                    + datetime.timedelta(seconds=seq)
                ).timestamp(),
            )
            if seq % 2 == 0:
                result[dst_file.normpath_str] = dst_file
            else:
                tmp = {}
                tmp[dst_file.normpath_str] = dst_file
                tmp.update(result)
                result = tmp

        return result

    @classmethod
    def get_files_in_date_range(
        cls,
        mtime_date_start: datetime.date,
        mtime_date_limit: datetime.date,
        path: str,
        *dirs: str,
        file_prefix: str = "TestFile",
        file_suffix: str = "",
        strftime: str = "_%Y-%m-%d",
        seq_num: int = 3,
        seq_num_sep: str = "_",
    ) -> dict[datetime.date, dict[str, FoundFile]]:
        result = {}
        one_day_delta = datetime.timedelta(days=1)
        target_date = mtime_date_start
        while target_date < mtime_date_limit:
            result[target_date] = cls.get_files(
                target_date,
                path,
                *dirs,
                file_prefix=file_prefix,
                file_suffix=file_suffix,
                strftime=strftime,
                seq_num=seq_num,
                seq_num_sep=seq_num_sep,
            )
            target_date += one_day_delta

        return result

    @classmethod
    def extract_file_latest(cls, dst_files: dict[str, FoundFile]) -> list[FoundFile]:
        for _, file in dst_files.items():
            result = file
            break

        for _, file in dst_files.items():
            if result.mtime < file.mtime:
                result = file

        return result

    @classmethod
    def extract_files_exclude_latest(
        cls, dst_files: dict[str, FoundFile]
    ) -> list[FoundFile]:
        result = []

        latest = None
        for _, file in dst_files.items():
            if latest is None:
                latest = file
            elif latest.mtime < file.mtime:
                result.append(latest)
                latest = file
            else:
                result.append(file)

        return result

    @classmethod
    def extract_files_exclude_latest_per_day(
        cls,
        date_file_dict: dict[datetime.date, dict[str, FoundFile]],
        mtime_date_start: datetime.date,
        mtime_date_limit: datetime.date,
    ) -> list[FoundFile]:
        result = []
        for date, item in date_file_dict.items():
            if mtime_date_start <= date and date < mtime_date_limit:
                result.extend(cls.extract_files_exclude_latest(item))

        return result

    @classmethod
    def concat(
        cls,
        date_file_dict: dict[datetime.date, dict[str, FoundFile]],
        mtime_date_start: datetime.date,
        mtime_date_limit: datetime.date,
    ) -> dict[str, FoundFile]:
        result = {}

        for date, item in date_file_dict.items():
            if mtime_date_start <= date and date < mtime_date_limit:
                result.update(item)

        return result
