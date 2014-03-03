import pytest
import ast
from annotators import *
from typing import *


@pytest.fixture
def annotator():
    return TypeAnnotator()


class TestTypeAnnotation:
    def setup_method(self, method):
        self.annotator = TypeAnnotator()
        self.ast = ast.parse(method.__doc__)
        self.ast = self.annotator.visit(self.ast)

    def testModuleScopeSingleAssignment(self):
        """
a = 2
        """
        assert self.ast.body[0].targets[0].typ == Int8
        assert self.ast.scope.find_symbol("a").typ == Int8

    def testFunctionScopeSingleAssignment(self):
        """
def test1(a : Int8):
    b = a
        """
        assert self.ast.body[0].body[0].targets[0].typ == Int8
        assert self.ast.body[0].body[0].scope.find_symbol("a").typ == Int8
        assert self.ast.body[0].scope.find_symbol("a").typ == Int8

    def testBinaryOperationInt8(self):
        """
def test1():
    a = 5
    b = 67
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == Int8
        assert self.ast.body[0].scope.find_symbol("a").typ == Int8
        assert self.ast.body[0].scope.find_symbol("b").typ == Int8
        assert self.ast.body[0].scope.find_symbol("c").typ == Int8

    def testBinaryOperationInt16(self):
        """
def test1():
    a = 5
    b = 62000
    c = a + b
        """
        assert self.ast.body[0].body[2].targets[0].typ == Int16
        assert self.ast.body[0].scope.find_symbol("a").typ == Int8
        assert self.ast.body[0].scope.find_symbol("b").typ == Int16
        assert self.ast.body[0].scope.find_symbol("c").typ == Int16
