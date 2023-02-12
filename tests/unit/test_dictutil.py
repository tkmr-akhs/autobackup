import pytest
import pytest_mock
import pytest_raises

from autobackup import dictutil


def test_recursive_merge_Simple():
    cnf = {"key1": "old value 1", "key2": "old value 2"}
    app_cnf = {"key3": "new value 3", "key2": "new value 2"}
    expected = {"key1": "old value 1", "key2": "new value 2", "key3": "new value 3"}

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_List():
    cnf = {"key": ["old value 1", "old value 2"]}
    app_cnf = {"key": ["new value"]}
    expected = {"key": ["new value"]}

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_Dict():
    cnf = {"key": {"key1": "old value 1", "key2": "old value 2"}}
    app_cnf = {"key": {"key3": "new value 3", "key2": "new value 2"}}
    expected = {
        "key": {"key1": "old value 1", "key2": "new value 2", "key3": "new value 3"}
    }

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_Dict2():
    cnf = {"key": {"key": {"key1": "old value 1", "key2": "old value 2"}}}
    app_cnf = {"key": {"key": {"key3": "new value 3", "key2": "new value 2"}}}
    expected = {
        "key": {
            "key": {"key1": "old value 1", "key2": "new value 2", "key3": "new value 3"}
        }
    }

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_DiffType():
    cnf = {"key": ["old value"]}
    app_cnf = {"key": {"key3": "new value 3", "key2": "new value 2"}}
    expected = {"key": {"key3": "new value 3", "key2": "new value 2"}}

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_IfNoneThenNotOverwrite():
    cnf = {"key": "old value"}
    app_cnf = {"key": None}
    expected = {"key": "old value"}

    dictutil.recursive_merge(cnf, app_cnf)

    assert cnf == expected


def test_recursive_merge_IfNoneWithFlagThenOverwrite():
    cnf = {"key": "old value"}
    app_cnf = {"key": None}
    expected = {"key": None}

    dictutil.recursive_merge(cnf, app_cnf, True)

    assert cnf == expected
