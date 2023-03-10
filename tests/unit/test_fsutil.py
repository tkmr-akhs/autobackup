import pytest
import pytest_mock
import pytest_raises
import pathlib
from os import sep

from autobackup import fsutil


class Test_FoundFile:
    @staticmethod
    def test_init_IfScanRootIsNoneThenParentOfFile(build_path):
        found_file = fsutil.FoundFile("/Path/To/File.ext", None)
        expected = pathlib.Path(build_path("/Path/To", file="File.ext")).parent

        actual = found_file.parent

        assert actual == expected

    @staticmethod
    def test_relpath_ReturnRelpath():
        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path")
        expected = pathlib.Path("To/File.ext")

        actual = found_file.relpath

        assert actual == expected

    @staticmethod
    def test_str_ReturnAbsolutePath(drive, build_path):
        import os

        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path")
        expected = "" + drive + sep + os.path.join("path", "To", "File.ext")

        actual = str(found_file)

        assert actual == expected

    @staticmethod
    def test_normpath_ReturnNormpathStr(drive, build_path):
        import os

        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path")
        expected = "" + drive + sep + os.path.join("path", "to", "file.ext")

        actual = found_file.normpath_str

        assert actual == expected

    @staticmethod
    def test_name_ReturnName():
        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path")
        expected = "File.ext"

        actual = found_file.name

        assert actual == expected

    @staticmethod
    def test_parent_ReturnParent(build_path):
        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path/To")
        expected = pathlib.Path(build_path("/Path/To"))

        actual = found_file.parent

        assert actual == expected

    @staticmethod
    def test_parent_ReturnParent2(build_path):
        found_file = fsutil.FoundFile("/Path/To/File.ext", "/Path")
        expected = pathlib.Path(build_path("/Path", "To"))

        actual = found_file.parent

        assert actual == expected

    @staticmethod
    def test_stem_ReturnStem():
        found_file = fsutil.FoundFile("/Path/To/.File.txt")

        actual = found_file.stem

        assert actual == ".File"

    @staticmethod
    def test_stem_IfFileNameStartsWithDotThenReturnStem():
        found_file = fsutil.FoundFile("/Path/To/.txt")

        actual = found_file.stem

        assert actual == ".txt"

    @staticmethod
    def test_suffix_ReturnNoSuffix():
        found_file = fsutil.FoundFile("/Path/To/.File.txt")

        actual = found_file.suffix

        assert actual == ".txt"

    @staticmethod
    def test_IfFileNameStartsWithDotThenReturnNoSuffix():
        found_file = fsutil.FoundFile("/Path/To/.txt")

        actual = found_file.suffix

        assert actual == ""

    @staticmethod
    def test_eq_IfEqualFoundFileThenReturnEquality():
        found_file1 = fsutil.FoundFile("/Path/To/File.ext")
        found_file2 = fsutil.FoundFile("/Path/To/File.ext")

        actual = found_file1 == found_file2

        assert actual == True

    @staticmethod
    def test_eq_IfEqualFoundFileThenReturnEquality2():
        found_file1 = fsutil.FoundFile("/Path/To/File.ext")
        found_file2 = fsutil.FoundFile("/Other/Path/To/File.ext")

        actual = found_file1 == found_file2

        assert actual == False

    @staticmethod
    def test_eq_IfEqualFoundFileThenReturnEquality3():
        found_file1 = fsutil.FoundFile("/Path/To/File.ext", "/Path/To")
        found_file2 = fsutil.FoundFile("/Path/To/File.ext", "/Path")

        actual = found_file1 == found_file2

        assert actual == False

    @staticmethod
    def test_eq_IfEqualPathThenReturnEquality():
        found_file = fsutil.FoundFile("/Path/To/File.ext")
        Path_obj = pathlib.Path("/Path/To/File.ext").absolute()

        actual = found_file == Path_obj

        assert actual == True

    @staticmethod
    def test_eq_IfEqualStrThenReturnEquality():
        import os

        found_file = fsutil.FoundFile("/Path/To/File.ext")
        path_str = os.path.abspath("/Path/To/File.ext")

        actual = found_file == path_str

        assert actual == True

    @staticmethod
    def test_eq_IfEqualBytesThenReturnEquality():
        found_file = fsutil.FoundFile("/Path/To/File.ext")
        path_bytes = bytes(pathlib.Path("/Path/To/File.ext").absolute())

        actual = found_file == path_bytes

        assert actual == True

    @staticmethod
    def test_eq_IfEqualOthersThenReturnFalse():
        found_file = fsutil.FoundFile("/Path/To/File.ext")
        other = object()

        actual = found_file == other

        assert actual == False

    @staticmethod
    def test_fspath_Fspath(build_path):
        import os

        found_file = fsutil.FoundFile("/Path/To/File.ext")

        actual = os.path.abspath(found_file)

        assert actual == os.path.abspath(build_path("/Path/To/", file="File.ext"))
