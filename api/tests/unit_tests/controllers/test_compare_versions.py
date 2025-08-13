import pytest

from controllers.console.version import _has_new_version


def add(*, first: int, second: int) -> int:
    return first + second


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (1, 1, 2),
        (2, 1, 3),
        (3, 1, 4),
        (4, 1, 5),
        (5, 1, 6),
        (6, 1, 7),
        (7, 1, 8),
        (8, 1, 9),
        (9, 1, 10),
        (10, 1, 11),
        (11, 1, 12),
    ],
)
def test_add(first, second, expected):
    assert add(first=first, second=second) == expected


@pytest.mark.parametrize(
    ("latest_version", "current_version", "expected"),
    [
        ("1.0.1", "1.0.0", True),
        ("1.1.0", "1.0.0", True),
        ("2.0.0", "1.9.9", True),
        ("1.0.0", "1.0.0", False),
        ("1.0.0", "1.0.1", False),
        ("1.0.0", "2.0.0", False),
        ("1.0.1", "1.0.0-beta", True),
        ("1.0.0", "1.0.0-alpha", True),
        ("1.0.0-beta", "1.0.0-alpha", True),
        ("1.0.0", "1.0.0-rc1", True),
        ("1.0.0", "0.9.9", True),
        ("1.0.0", "1.0.0-dev", True),
    ],
)
def test_has_new_version(latest_version, current_version, expected):
    """
    测试版本比较函数_has_new_version的正确性

    该测试函数使用参数化测试来验证不同版本号组合的比较结果是否符合预期

    参数:
        latest_version (str): 最新版本号字符串
        current_version (str): 当前版本号字符串
        expected (bool): 预期的比较结果，True表示有新版本，False表示无新版本

    返回值:
        无返回值，通过断言验证函数执行结果是否与预期一致
    """
    # 使用断言验证版本比较函数的返回值是否与预期结果一致
    assert (
        _has_new_version(latest_version=latest_version, current_version=current_version)
        == expected
    )
