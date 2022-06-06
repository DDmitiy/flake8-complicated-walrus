import ast
from typing import List

from flake8_complicated_walrus import FCW100, FCW200, Plugin, RestrictWalrusLevels


def lint_code(loc: str, restrict_walrus_level: RestrictWalrusLevels) -> List[str]:
    tree = ast.parse(loc)
    plugin = Plugin(tree)
    plugin._restrict_walrus_level = restrict_walrus_level
    return [f'{line}:{col} {message}' for line, col, message, _ in plugin.run()]


def test_complex_if():
    errors = lint_code('if (a:=10) and True: pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert len(errors) == 1
    assert FCW200 in errors[0]


def test_if():
    errors = lint_code('if a:=10: pass', RestrictWalrusLevels.RESTRICT_ALL)
    assert len(errors) == 1
    assert FCW100 in errors[0]


def test_if_with_func():
    errors = lint_code('if all(True): pass', RestrictWalrusLevels.RESTRICT_ALL)
    assert not errors


def test_if_with_negative():
    errors = lint_code('if not (a:=10): pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert len(errors) == 1
    assert FCW200 in errors[0]


def test_if_with_is_none():
    errors = lint_code('if (a:=10) is None: pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert len(errors) == 1
    assert FCW200 in errors[0]


def test_if_with_is_not_none():
    errors = lint_code('if (a:=10) is not None: pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert len(errors) == 1
    assert FCW200 in errors[0]


def test_if_with_compare_values():
    errors = lint_code('if (a:=10) == 10: pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert len(errors) == 1
    assert FCW200 in errors[0]


def test_common_while():
    errors = lint_code('while a:=0: pass', RestrictWalrusLevels.RESTRICT_COMPLICATED)
    assert not errors
