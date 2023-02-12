import pytest
import pytest_mock
import pytest_raises
import datetime
import os
import pathlib
import platform
import shutil
import subprocess

import tests.testutil as testutil
from autobackup.fsutil import FoundFile
from autobackup.scanner import AllFileScanner


@pytest.fixture
def drive() -> str:
    return pathlib.Path(".").absolute().drive


@pytest.fixture
def testdata_timestamp() -> float:
    return testutil.TESTDATA_TIMESTAMP


def _create_testdir(dirname: str) -> pathlib.Path:

    test_tmp_path = pathlib.Path("tests", "tmp")
    if not test_tmp_path.exists():
        test_tmp_path.mkdir()

    testdata_rootpath = test_tmp_path.joinpath(dirname)
    if testdata_rootpath.is_file():
        testdata_rootpath.unlink()
    elif testdata_rootpath.is_dir():
        shutil.rmtree(testdata_rootpath)

    testdata_rootpath.mkdir()

    return testdata_rootpath


def _create_src_files(testdata_rootpath: pathlib.Path) -> pathlib.Path:
    # tests/tmp/*/testdir
    #  |
    #  +- testdir1
    #  |   +- testfile11
    #  |   +- testfile12.ext
    #  |
    #  +- testdir2
    #  |   +- .testfile21
    #  |   +- testfile21
    #  |
    #  +- testfile
    #
    # st_mtime of file = 2023-01-23 04:56:12.345678

    timestamp = testutil.TESTDATA_TIMESTAMP

    testdir_path = testdata_rootpath.joinpath("TestDir")
    testdir1_path = testdir_path.joinpath("TestDir1")
    testdir2_path = testdir_path.joinpath("TestDir2")
    testfile_path = testdir_path.joinpath("TestFile")
    testfile11_path = testdir1_path.joinpath("TestFile11")
    testfile12_path = testdir1_path.joinpath("TestFile12.ext")
    testfile21_path = testdir2_path.joinpath(".TestFile21")
    testfile22_path = testdir2_path.joinpath("TestFile22")

    testdir_path.mkdir()
    testdir1_path.mkdir()
    testdir2_path.mkdir()
    testfile_path.touch()
    testfile11_path.touch()
    testfile12_path.touch()
    testfile21_path.touch()
    testfile22_path.touch()

    os.utime(testfile_path, (timestamp, timestamp))
    os.utime(testfile11_path, (timestamp, timestamp))
    os.utime(testfile12_path, (timestamp, timestamp))
    os.utime(testfile21_path, (timestamp, timestamp))
    os.utime(testfile22_path, (timestamp, timestamp))

    if platform.system() == "Windows":
        subprocess.check_call(["attrib", "+H", testfile21_path])

    return testdir_path


def _create_dst_files(testdir_path: pathlib.Path) -> None:
    timestamp = testutil.TESTDATA_TIMESTAMP
    src_testfile_path = testdir_path.joinpath("TestFile")
    src_testfile11_path = testdir_path.joinpath("TestDir1", "TestFile11")
    src_testfile12_path = testdir_path.joinpath("TestDir1", "TestFile12.ext")
    src_testfile21_path = testdir_path.joinpath("TestDir2", ".TestFile21")
    src_testfile22_path = testdir_path.joinpath("TestDir2", "TestFile22")

    dst_testdir_path = testdir_path.joinpath(".old")
    dst_testdir1_path = testdir_path.joinpath("TestDir1", ".old")
    dst_testdir2_path = testdir_path.joinpath("TestDir2", ".old")
    dst_testfile_path = dst_testdir_path.joinpath(
        f"TestFile{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile11_path = dst_testdir1_path.joinpath(
        f"TestFile11{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile12_path = dst_testdir1_path.joinpath(
        f"TestFile12{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000.ext"
    )
    dst_testfile21_path = dst_testdir2_path.joinpath(
        f".TestFile21{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile22_path = dst_testdir2_path.joinpath(
        f"TestFile22{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )

    dst_testdir_path.mkdir()
    dst_testdir1_path.mkdir()
    dst_testdir2_path.mkdir()
    shutil.copy2(src_testfile_path, dst_testfile_path)
    shutil.copy2(src_testfile11_path, dst_testfile11_path)
    shutil.copy2(src_testfile12_path, dst_testfile12_path)
    shutil.copy2(src_testfile21_path, dst_testfile21_path)
    shutil.copy2(src_testfile22_path, dst_testfile22_path)


def _create_dst_files_noseq(testdir_path: pathlib.Path) -> None:
    timestamp = testutil.TESTDATA_TIMESTAMP
    src_testfile_path = testdir_path.joinpath("TestFile")
    src_testfile11_path = testdir_path.joinpath("TestDir1", "TestFile11")
    src_testfile12_path = testdir_path.joinpath("TestDir1", "TestFile12.ext")
    src_testfile21_path = testdir_path.joinpath("TestDir2", ".TestFile21")
    src_testfile22_path = testdir_path.joinpath("TestDir2", "TestFile22")

    dst_testdir_path = testdir_path.joinpath(".old")
    dst_testdir1_path = testdir_path.joinpath("TestDir1", ".old")
    dst_testdir2_path = testdir_path.joinpath("TestDir2", ".old")
    dst_testfile_path = dst_testdir_path.joinpath(
        f"TestFile{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile11_path = dst_testdir1_path.joinpath(
        f"TestFile11{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile12_path = dst_testdir1_path.joinpath(
        f"TestFile12{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}.ext"
    )
    dst_testfile21_path = dst_testdir2_path.joinpath(
        f".TestFile21{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile22_path = dst_testdir2_path.joinpath(
        f"TestFile22{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )

    dst_testdir_path.mkdir()
    dst_testdir1_path.mkdir()
    dst_testdir2_path.mkdir()
    shutil.copy2(src_testfile_path, dst_testfile_path)
    shutil.copy2(src_testfile11_path, dst_testfile11_path)
    shutil.copy2(src_testfile12_path, dst_testfile12_path)
    shutil.copy2(src_testfile21_path, dst_testfile21_path)
    shutil.copy2(src_testfile22_path, dst_testfile22_path)


def _outdate_dst_files(testdir_path: pathlib.Path) -> None:
    timestamp = testutil.TESTDATA_TIMESTAMP - 0.001

    dst_testfile_path = testdir_path.joinpath(
        ".old",
        f"TestFile{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile11_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile11{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile12_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile12{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000.ext",
    )
    dst_testfile21_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f".TestFile21{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile22_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f"TestFile22{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )

    os.utime(dst_testfile_path, (timestamp, timestamp))
    os.utime(dst_testfile11_path, (timestamp, timestamp))
    os.utime(dst_testfile12_path, (timestamp, timestamp))
    os.utime(dst_testfile21_path, (timestamp, timestamp))
    os.utime(dst_testfile22_path, (timestamp, timestamp))


def _outdate_dst_files_noseq(testdir_path: pathlib.Path) -> None:
    timestamp = testutil.TESTDATA_TIMESTAMP - 0.001

    dst_testfile_path = testdir_path.joinpath(
        ".old",
        f"TestFile{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile11_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile11{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile12_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile12{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}.ext",
    )
    dst_testfile21_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f".TestFile21{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile22_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f"TestFile22{datetime.datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )

    os.utime(dst_testfile_path, (timestamp, timestamp))
    os.utime(dst_testfile11_path, (timestamp, timestamp))
    os.utime(dst_testfile12_path, (timestamp, timestamp))
    os.utime(dst_testfile21_path, (timestamp, timestamp))
    os.utime(dst_testfile22_path, (timestamp, timestamp))


@pytest.fixture
def testdir() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        return str(testdata_root_path)

    return _func


@pytest.fixture
def testdata() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        testdir_path = _create_src_files(testdata_root_path)
        return str(testdir_path)

    return _func


@pytest.fixture
def testdata_fresh() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        testdir_path = _create_src_files(testdata_root_path)
        _create_dst_files(testdir_path)
        return str(testdir_path)

    return _func


@pytest.fixture
def testdata_fresh_noseq() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        testdir_path = _create_src_files(testdata_root_path)
        _create_dst_files_noseq(testdir_path)
        return str(testdir_path)

    return _func


@pytest.fixture
def testdata_stale() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        testdir_path = _create_src_files(testdata_root_path)
        _create_dst_files(testdir_path)
        _outdate_dst_files(testdir_path)
        return str(testdir_path)

    return _func


@pytest.fixture
def testdata_stale_noseq() -> None:
    def _func(dirname: str) -> str:
        testdata_root_path = _create_testdir(dirname)
        testdir_path = _create_src_files(testdata_root_path)
        _create_dst_files_noseq(testdir_path)
        _outdate_dst_files_noseq(testdir_path)
        return str(testdir_path)

    return _func


@pytest.fixture
def FoundFileMock():
    class _FoundFileMock(FoundFile):
        def __init__(
            self, filepath: str, scan_root_dirpath: str = None, mtime: float = 0.0
        ) -> None:
            super().__init__(filepath, scan_root_dirpath)
            self._mtime = mtime

        @property
        def mtime(self) -> float:
            return self._mtime

    return _FoundFileMock


@pytest.fixture
def AllFileScannerMock():
    class _AllFileScannerMock(AllFileScanner):
        def __init__(self, targets=None, all_files: dict[str, FoundFile] = {}) -> None:
            super().__init__(targets)
            self._all_files = all_files

        def get_all_files(self) -> dict[str, FoundFile]:
            return self._all_files

    return _AllFileScannerMock


@pytest.fixture
def rscan():
    return testutil.rscan


@pytest.fixture
def build_path():
    return testutil.build_path


@pytest.fixture
def testpath():
    return testutil.testpath
