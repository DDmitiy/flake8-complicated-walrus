import ast
import sys
from enum import Enum
from typing import Any, Generator, Type

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


FCW100 = 'FCW100: You cannot use assignment expression.'
FCW200 = 'FCW200: You cannot use assignment expression in complicated if statements.'


class RestrictWalrusLevels(str, Enum):
    RESTRICT_ALL = 'restrict-all'
    RESTRICT_COMPLICATED = 'restrict-complicated'
    ALLOW_ALL = 'allow-all'


class Visitor(ast.NodeVisitor):
    def __init__(self, restrict_walrus_level: RestrictWalrusLevels) -> None:
        self._restrict_walrus_level = restrict_walrus_level
        self.errors: list[tuple[int, int, str]] = []

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        if self._restrict_walrus_level == RestrictWalrusLevels.RESTRICT_ALL:
            self.errors.append((node.lineno, node.col_offset, FCW100))
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if self._restrict_walrus_level != RestrictWalrusLevels.RESTRICT_COMPLICATED:
            self.generic_visit(node)
            return

        if isinstance(node.test, ast.Compare):
            values = [node.test.left] + node.test.comparators
            has_named_expr = any(isinstance(test_node, ast.NamedExpr) for test_node in values)
            if has_named_expr:
                self.errors.append((node.lineno, node.col_offset, FCW200))

        if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.operand, ast.NamedExpr):
            self.errors.append((node.lineno, node.col_offset, FCW200))

        if isinstance(node.test, ast.BoolOp) and len(node.test.values) > 1:
            has_named_expr = any(isinstance(test_node, ast.NamedExpr) for test_node in node.test.values)
            if has_named_expr:
                self.errors.append((node.lineno, node.col_offset, FCW200))

        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    restrict_walrus_option_shortname_for_cli = 'rwl'
    restrict_walrus_option_fullname_for_cli = 'restrict-walrus-level'
    restrict_walrus_option_name_for_conf = 'restrict_walrus_level'
    default_restrict_walrus_level = RestrictWalrusLevels.RESTRICT_COMPLICATED

    @classmethod
    def add_options(cls, parser):
        """Required by flake8
        add the possible options, called first
        Args:
            parser (OptionsManager):
        """
        kwargs = {'action': 'store', 'parse_from_config': True}
        parser.add_option(
            f'-{cls.restrict_walrus_option_shortname_for_cli}',
            f'--{cls.restrict_walrus_option_fullname_for_cli}',
            default=cls.default_restrict_walrus_level,
            **kwargs,
        )

    @classmethod
    def parse_options(cls, options):
        """Required by flake8
        parse the options, called after add_options
        Args:
            options (dict): options to be parsed
        """
        cls._restrict_walrus_level = RestrictWalrusLevels(
            getattr(
                options,
                cls.restrict_walrus_option_name_for_conf,
                cls.default_restrict_walrus_level,
            ).lower()
        )

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, Type[Any]], None, None]:
        """
        Any module from specified package could not be import in another package
        """
        visitor = Visitor(self._restrict_walrus_level)
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
