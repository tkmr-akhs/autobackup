import pytest
import pytest_mock
import pytest_raises
import os
import pathlib
import platform
import shutil
import subprocess


from datetime import date, datetime
from autobackup.fsutil import FoundFile
from autobackup.scanner import AllFileScanner
import tests.testutil as testutil

DUMMY_SCAN_ROOT = "/Path/To/TestDir"


def pytest_generate_tests(metafunc):
    if "test_prarams_for_get_discard_list" in metafunc.fixturenames:
        metafunc.parametrize(
            "test_prarams_for_get_discard_list",
            list(_build_test_params_for_get_discard_list()),
        )


@pytest.fixture
def drive() -> str:
    return pathlib.Path(".").absolute().drive


@pytest.fixture
def testdata_timestamp() -> float:
    return testutil.TESTDATA_TIMESTAMP


@pytest.fixture
def dummyfile():
    return testutil.dummyfile


@pytest.fixture
def dummy_testdata():
    return (DUMMY_SCAN_ROOT, _create_src_dummy_files())


@pytest.fixture
def dummy_testdata_fresh():
    result = _create_src_dummy_files()
    result.update(_create_dst_dummy_files(testutil.TESTDATA_TIMESTAMP))
    return (DUMMY_SCAN_ROOT, result)


@pytest.fixture
def dummy_testdata_fresh_noseq():
    result = _create_src_dummy_files()
    result.update(_create_dst_dummy_files_noseq(testutil.TESTDATA_TIMESTAMP))
    return (DUMMY_SCAN_ROOT, result)


@pytest.fixture
def dummy_testdata_satle():
    result = _create_src_dummy_files()
    result.update(_create_dst_dummy_files(testutil.TESTDATA_TIMESTAMP - 0.001))
    return (DUMMY_SCAN_ROOT, result)


@pytest.fixture
def dummy_testdata_stale_noseq():
    result = _create_src_dummy_files()
    result.update(_create_dst_dummy_files_noseq(testutil.TESTDATA_TIMESTAMP - 0.001))
    return _create_src_dummy_files(DUMMY_SCAN_ROOT, result)


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


def _create_src_dummy_files() -> dict[str, FoundFile]:
    from tests.testutil import dummyfile, build_path, TESTDATA_TIMESTAMP

    mtime = TESTDATA_TIMESTAMP
    target_dir = DUMMY_SCAN_ROOT
    src_testfile_key = build_path(target_dir, file="testfile")
    src_testfile = dummyfile.get_file(
        target_dir,
        file_prefix="TestFile",
        mtime=mtime,
    )
    src_testfile11_key = build_path(target_dir, "testdir1", file="testfile11")
    src_testfile11 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        file_prefix="TestFile11",
        mtime=mtime,
    )
    src_testfile12_key = build_path(target_dir, "testdir1", file="testfile12.ext")
    src_testfile12 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        file_prefix="TestFile12",
        file_suffix=".ext",
        mtime=mtime,
    )
    src_testfile21_key = build_path(target_dir, "testdir2", file=".testfile21")
    src_testfile21 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        file_prefix=".TestFile21",
        mtime=mtime,
        is_hidden_flag=True,
    )
    src_testfile22_key = build_path(target_dir, "testdir2", file="testfile22")
    src_testfile22 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        file_prefix="TestFile22",
        mtime=mtime,
    )

    return {
        src_testfile_key: src_testfile,
        src_testfile11_key: src_testfile11,
        src_testfile12_key: src_testfile12,
        src_testfile21_key: src_testfile21,
        src_testfile22_key: src_testfile22,
    }


def _create_dst_dummy_files(mtime: float) -> dict[str, FoundFile]:
    from tests.testutil import dummyfile, build_path, TESTDATA_TIMESTAMP

    mtime_str = datetime.fromtimestamp(mtime).strftime("_%Y-%m-%d")
    target_dir = DUMMY_SCAN_ROOT
    dst_testfile_key = build_path(target_dir, ".old", file=f"testfile{mtime_str}_0000")
    dst_testfile = dummyfile.get_file(
        target_dir,
        ".old",
        file_prefix="TestFile",
        strftime="_%Y-%m-%d",
        seq_num_sep="_",
        mtime=mtime,
    )
    dst_testfile11_key = build_path(
        target_dir, "testdir1", ".old", file=f"testfile11{mtime_str}_0000"
    )
    dst_testfile11 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        ".old",
        file_prefix="TestFile11",
        strftime="_%Y-%m-%d",
        seq_num_sep="_",
        mtime=mtime,
    )
    dst_testfile12_key = build_path(
        target_dir, "testdir1", ".old", file=f"testfile12{mtime_str}_0000.ext"
    )
    dst_testfile12 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        ".old",
        file_prefix="TestFile12",
        file_suffix=".ext",
        strftime="_%Y-%m-%d",
        seq_num_sep="_",
        mtime=mtime,
    )
    dst_testfile21_key = build_path(
        target_dir, "testdir2", ".old", file=f".testfile21{mtime_str}_0000"
    )
    dst_testfile21 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        ".old",
        file_prefix=".TestFile21",
        strftime="_%Y-%m-%d",
        seq_num_sep="_",
        mtime=mtime,
        is_hidden_flag=True,
    )
    dst_testfile22_key = build_path(
        target_dir, "testdir2", ".old", file=f"testfile22{mtime_str}_0000"
    )
    dst_testfile22 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        ".old",
        file_prefix="TestFile22",
        strftime="_%Y-%m-%d",
        seq_num_sep="_",
        mtime=mtime,
    )

    return {
        dst_testfile_key: dst_testfile,
        dst_testfile11_key: dst_testfile11,
        dst_testfile12_key: dst_testfile12,
        dst_testfile21_key: dst_testfile21,
        dst_testfile22_key: dst_testfile22,
    }


def _create_dst_dummy_files_noseq(mtime: float) -> dict[str, FoundFile]:
    from tests.testutil import dummyfile, build_path, TESTDATA_TIMESTAMP

    mtime_str = datetime(mtime).strftime("_%Y-%m-%d")
    target_dir = DUMMY_SCAN_ROOT
    dst_testfile_key = build_path(target_dir, ".old", file=f"testfile{mtime_str}")
    dst_testfile = dummyfile.get_file(
        target_dir,
        file_prefix="TestFile",
        strftime="_%Y-%m-%d",
        mtime=mtime,
    )
    dst_testfile11_key = build_path(
        target_dir, ".old", "testdir1", file=f"testfile11{mtime_str}"
    )
    dst_testfile11 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        file_prefix="TestFile11",
        strftime="_%Y-%m-%d",
        mtime=mtime,
    )
    dst_testfile12_key = build_path(
        target_dir, ".old", "testdir1", file=f"testfile12{mtime_str}.ext"
    )
    dst_testfile12 = dummyfile.get_file(
        target_dir,
        "TestDir1",
        file_prefix="TestFile12",
        file_suffix=".ext",
        strftime="_%Y-%m-%d",
        mtime=mtime,
    )
    dst_testfile21_key = build_path(
        target_dir, ".old", "testdir2", file=f".testfile21{mtime_str}"
    )
    dst_testfile21 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        file_prefix=".TestFile21",
        strftime="_%Y-%m-%d",
        mtime=mtime,
        is_hidden_flag=True,
    )
    dst_testfile22_key = build_path(
        target_dir, ".old", "testdir2", file=f"testfile22{mtime_str}"
    )
    dst_testfile22 = dummyfile.get_file(
        target_dir,
        "TestDir2",
        file_prefix="TestFile22",
        strftime="_%Y-%m-%d",
        mtime=mtime,
    )

    return {
        dst_testfile_key: dst_testfile,
        dst_testfile11_key: dst_testfile11,
        dst_testfile12_key: dst_testfile12,
        dst_testfile21_key: dst_testfile21,
        dst_testfile22_key: dst_testfile22,
    }


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
        f"TestFile{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile11_path = dst_testdir1_path.joinpath(
        f"TestFile11{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile12_path = dst_testdir1_path.joinpath(
        f"TestFile12{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000.ext"
    )
    dst_testfile21_path = dst_testdir2_path.joinpath(
        f".TestFile21{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
    )
    dst_testfile22_path = dst_testdir2_path.joinpath(
        f"TestFile22{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000"
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
        f"TestFile{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile11_path = dst_testdir1_path.joinpath(
        f"TestFile11{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile12_path = dst_testdir1_path.joinpath(
        f"TestFile12{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}.ext"
    )
    dst_testfile21_path = dst_testdir2_path.joinpath(
        f".TestFile21{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
    )
    dst_testfile22_path = dst_testdir2_path.joinpath(
        f"TestFile22{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}"
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
        f"TestFile{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile11_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile11{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile12_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile12{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000.ext",
    )
    dst_testfile21_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f".TestFile21{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
    )
    dst_testfile22_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f"TestFile22{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}_0000",
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
        f"TestFile{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile11_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile11{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile12_path = testdir_path.joinpath(
        "TestDir1",
        ".old",
        f"TestFile12{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}.ext",
    )
    dst_testfile21_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f".TestFile21{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )
    dst_testfile22_path = testdir_path.joinpath(
        "TestDir2",
        ".old",
        f"TestFile22{datetime.fromtimestamp(timestamp).strftime('_%Y-%m-%d')}",
    )

    os.utime(dst_testfile_path, (timestamp, timestamp))
    os.utime(dst_testfile11_path, (timestamp, timestamp))
    os.utime(dst_testfile12_path, (timestamp, timestamp))
    os.utime(dst_testfile21_path, (timestamp, timestamp))
    os.utime(dst_testfile22_path, (timestamp, timestamp))


def _build_test_params_for_get_discard_list() -> list[
    tuple[date, dict[str, FoundFile], list[FoundFile]]
]:
    from tests.testutil import dummyfile

    TARGET_PATH = DUMMY_SCAN_ROOT

    # ---------------------------------------------------------------------------------
    # If today is 1/23 on 2023 and the mtime of the file is from 2023-01-7 to 2023-01-10,
    today = date(2023, 1, 23)
    files_in_range = dummyfile.get_files_in_date_range(
        date(2023, 1, 7), date(2023, 1, 11), TARGET_PATH, ".old", strftime="_%Y-%m-%d"
    )
    dst_files = {}
    for _, dst_files_in_date in files_in_range.items():
        dst_files.update(dst_files_in_date)
    # 1/7 and 1/8 are discarded, leaving the latest files. Files after that date are kept.
    expected = []
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2023, 1, 7)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2023, 1, 8)])
    )
    yield (today, dst_files, expected)
    today = None
    dst_files = None
    expected = None

    # ---------------------------------------------------------------------------------
    # If today is 1/22 on 2023 and the mtime of the file is from 2022-12-31 to 2023-01-10,
    today = date(2023, 1, 22)
    files_in_range = dummyfile.get_files_in_date_range(
        date(2022, 12, 31), date(2023, 1, 11), TARGET_PATH, ".old", strftime="_%Y-%m-%d"
    )
    dst_files = {}
    for _, dst_files_in_date in files_in_range.items():
        dst_files.update(dst_files_in_date)
    # 12/31 and 1/1 are discarded, leaving the latest files. Files after that date are kept.
    expected = []
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 12, 31)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2023, 1, 1)])
    )
    yield (today, dst_files, expected)
    today = None
    dst_files = None
    expected = None

    # ---------------------------------------------------------------------------------
    # If today is 1/1 on 2023 and the mtime of the file is from 2022-10-23 to 2022-11-02,
    today = date(2023, 1, 1)
    files_in_range = dummyfile.get_files_in_date_range(
        date(2022, 10, 23), date(2022, 11, 3), TARGET_PATH, ".old", strftime="_%Y-%m-%d"
    )
    dst_files = {}
    for _, dst_files_in_date in files_in_range.items():
        dst_files.update(dst_files_in_date)
    # from 10/23 to 10/31 are discarded, leaving the latest files per week.
    # from 10/1 to 11/2 are discarded, leaving the latest files per day.
    expected = []
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 10, 23)])
    )
    expected.extend(
        dummyfile.concat(
            files_in_range, date(2022, 10, 24), date(2022, 10, 30)
        ).values()
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 10, 30)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 10, 31)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 11, 1)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 11, 2)])
    )
    yield (today, dst_files, expected)
    today = None
    dst_files = None
    expected = None

    # ---------------------------------------------------------------------------------
    # If today is 12/31 on 2022 and the mtime of the file is from 2022-09-18 to 2022-11-02,
    today = date(2022, 12, 31)
    files_in_range = dummyfile.get_files_in_date_range(
        date(2022, 9, 18), date(2022, 11, 3), TARGET_PATH, ".old", strftime="_%Y-%m-%d"
    )
    dst_files = {}
    for _, dst_files_in_date in files_in_range.items():
        dst_files.update(dst_files_in_date)
    # from 9/18 to 9/30 are discarded, leaving the latest files per week.
    # from 10/1 to 11/2 are discarded, leaving the latest files per day.
    expected = []
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 9, 18)])
    )
    expected.extend(
        dummyfile.concat(files_in_range, date(2022, 9, 19), date(2022, 9, 25)).values()
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 9, 25)])
    )
    expected.extend(
        dummyfile.concat(files_in_range, date(2022, 9, 26), date(2022, 9, 30)).values()
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest(files_in_range[date(2022, 9, 30)])
    )
    expected.extend(
        dummyfile.extract_files_exclude_latest_per_day(
            files_in_range, date(2022, 10, 1), date(2022, 11, 3)
        )
    )
    yield (today, dst_files, expected)
    today = None
    dst_files = None
    expected = None
