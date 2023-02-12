import datetime
import os
import pathlib

TESTDATA_TIMESTAMP = datetime.datetime(2023, 1, 23, 4, 56, 12, 345678).timestamp()


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
        if norm_dir:
            result = os.path.join(result, os.path.normcase(dir))
        else:
            result = os.path.join(result, dir)

    if file == None:
        file = ""

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
