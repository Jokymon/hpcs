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


class TestSymbolLookup:
    def testEmptyScopeStack(self, annotator):
        assert annotator.lookup_symbol("unknown_id") == None

    def testNonexistingSymbol(self, annotator):
        annotator.push_scope()
        sym = Symbol("aname")
        annotator.add_symbol_to_top_scope(sym)
        assert annotator.lookup_symbol("anothername") == None

    def testSymbolInTopScope(self, annotator):
        annotator.push_scope()
        sym = Symbol("aname")
        annotator.add_symbol_to_top_scope(sym)
        assert annotator.lookup_symbol("aname") != None

    def testSymbolInNestedScope(self, annotator):
        annotator.push_scope()
        sym = Symbol("nestedname")
        annotator.add_symbol_to_top_scope(sym)
        annotator.push_scope()
        assert annotator.lookup_symbol("nestedname") != None

    def testSymbolAfterNestedScope(self, annotator):
        annotator.push_scope()
        sym = Symbol("nestedname")
        annotator.add_symbol_to_top_scope(sym)
        annotator.push_scope()
        sym = Symbol("topname")
        annotator.add_symbol_to_top_scope(sym)
        annotator.pop_scope()
        assert annotator.lookup_symbol("nestedname") != None



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
        assert self.annotator.lookup_symbol("a").typ == UInt8

    def testFunctionScopeSingleAssignment(self):
        """
def test1(a : int):
    b = a
        """
        assert self.ast.body[0].body[0].targets[0].typ == int

    def testBinaryOperationUInt8(self):
        """
def test1():
    a = 5
    b = 67
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == UInt8

    def testBinaryOperationUInt16(self):
        """
def test1():
    a = 5
    b = 62000
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == UInt16
