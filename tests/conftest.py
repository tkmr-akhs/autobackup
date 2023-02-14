import pytest
import pytest_mock
import pytest_raises
import datetime
import os
import pathlib
import platform
import shutil
import subprocess

from autobackup.fsutil import FoundFile
from autobackup.scanner import AllFileScanner
import tests.testutil as testutil


def pytest_generate_tests(metafunc):
    if "test_prarams_for_get_discard_list" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_prarams_for_get_discard_list",
            list(_build_test_params_for_get_discard_list()),
        )


def _build_test_params_for_get_discard_list() -> list[
    tuple[datetime.date, dict[str, FoundFile], list[FoundFile]]
]:
    # ---------------------------------------------------------------------------------
    # If today is 1/23 on 2023 and the mtime of the file is from 2023-01-7 to 2023-01-10,
    today = datetime.date(2023, 1, 23)
    dst_files_in_date_range = testutil.dummy_found_files.get_files_in_date_range(
        datetime.date(2023, 1, 7), datetime.date(2023, 1, 11), dst_dirname=".old"
    )
    dst_files = {}
    for _, dst_files_in_date in dst_files_in_date_range.items():
        dst_files.update(dst_files_in_date)
    # 1/7 and 1/8 are discarded, leaving the latest files. Files after that date are kept.
    expected = []
    expected.extend(
        testutil.dummy_found_files.get_files_exclude_latest(
            dst_files_in_date_range[datetime.date(2023, 1, 7)]
        )
    )
    expected.extend(
        testutil.dummy_found_files.get_files_exclude_latest(
            dst_files_in_date_range[datetime.date(2023, 1, 8)]
        )
    )
    yield (today, dst_files, expected)

    # ---------------------------------------------------------------------------------
    # If today is 1/22 on 2023 and the mtime of the file is from 2022-12-31 to 2023-01-10,
    today = datetime.date(2023, 1, 22)
    dst_files_in_date_range = testutil.dummy_found_files.get_files_in_date_range(
        datetime.date(2022, 12, 31), datetime.date(2023, 1, 11), dst_dirname=".old"
    )
    dst_files = {}
    for _, dst_files_in_date in dst_files_in_date_range.items():
        dst_files.update(dst_files_in_date)
    # 12/31 and 1/1 are discarded, leaving the latest files. Files after that date are kept.
    expected = []
    expected.extend(
        testutil.dummy_found_files.get_files_exclude_latest(
            dst_files_in_date_range[datetime.date(2022, 12, 31)]
        )
    )
    expected.extend(
        testutil.dummy_found_files.get_files_exclude_latest(
            dst_files_in_date_range[datetime.date(2023, 1, 1)]
        )
    )
    yield (today, dst_files, expected)


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
    return testutil.FoundFileMock


@pytest.fixture
def AllFileScannerMock():
    return testutil.AllFileScannerMock


@pytest.fixture
def rscan():
    return testutil.rscan


@pytest.fixture
def build_path():
    return testutil.build_path


@pytest.fixture
def testpath():
    return testutil.testpath
