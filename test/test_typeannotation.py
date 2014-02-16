import pytest
import ast
from annotators import *
from typing import *


@pytest.fixture
def annotator():
    return TypeAnnotator()


class TestSymbolTable:
    def testEmptyTable(self):
        tab = SymbolTable(None)
        assert tab.find_symbol("unknown_id") == None

    def testExistingSymbol(self):
        tab = SymbolTable(None)
        tab.add_symbol(Symbol("aname", None))
        assert tab.find_symbol("aname") is not None

    def testFindNestedSymbol(self):
        tab = SymbolTable(None)
        nested_tab = SymbolTable(tab)

        tab.add_symbol(Symbol("aname", None))
        assert nested_tab.find_symbol("aname") is not None


class TestTypeAnnotation:
    def setup_method(self, method):
        self.annotator = TypeAnnotator()
        self.ast = ast.parse(method.__doc__)
        self.ast = self.annotator.visit(self.ast)

    def testModuleScopeSingleAssignment(self):
        """
a = 2
        """
        assert self.ast.body[0].targets[0].typ == UInt8
        assert self.ast.scope.find_symbol("a").typ == UInt8

    def testFunctionScopeSingleAssignment(self):
        """
def test1(a : int):
    b = a
        """
        assert self.ast.body[0].body[0].targets[0].typ == int
        assert self.ast.body[0].body[0].scope.find_symbol("a").typ == int
        assert self.ast.body[0].scope.find_symbol("a").typ == int

    def testBinaryOperationUInt8(self):
        """
def test1():
    a = 5
    b = 67
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == UInt8
        assert self.ast.body[0].scope.find_symbol("a").typ == UInt8
        assert self.ast.body[0].scope.find_symbol("b").typ == UInt8
        assert self.ast.body[0].scope.find_symbol("c").typ == UInt8

    def testBinaryOperationUInt16(self):
        """
def test1():
    a = 5
    b = 62000
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == UInt16
        assert self.ast.body[0].scope.find_symbol("a").typ == UInt8
        assert self.ast.body[0].scope.find_symbol("b").typ == UInt16
        assert self.ast.body[0].scope.find_symbol("c").typ == UInt16
