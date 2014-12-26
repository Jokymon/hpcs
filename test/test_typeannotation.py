import pytest
import ast
import symtab
import hpcs_builtins
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

    def testBinaryComparison(self):
        """
a = 34 < 59
        """
        assert self.ast.scope.find_symbol("a").typ == Bool()

    def testStringAssignment(self):
        """
s = "Some string"
        """
        assert self.ast.body[0].scope.find_symbol("s").typ == String()

    def testCharacterFromString(self):
        """
s = "A string"
c = s[3]
        """
        assert self.ast.body[0].scope.find_symbol("c").typ == Int8

    def testCallTypeAnnotation(self):
        """
def return_int8(a : Int8) -> Int8:
    return 2*a

b = return_int8(3)
        """
        assert self.ast.body[0].scope.find_symbol("b").typ == Int8


class TestCustomTypeAnnotation:
    def setup_method(self, method):
        self.ast = ast.parse(method.__doc__)

    def testBuiltins(self):
        """
a = max(53, 45)
        """
        builtins = symtab.SymbolTable(None)
        builtins.add_symbol(symtab.Symbol("max",
                                          Function(Int32, [Int32, Int32])))

        annotator = TypeAnnotator(builtins)
        self.ast = annotator.visit(self.ast)
        assert self.ast.body[0].scope.find_symbol("a").typ == Int32


class TestArray:
    def setup_method(self, method):
        self.annotator = TypeAnnotator(hpcs_builtins.create_builtin_scope())
        self.ast = ast.parse(method.__doc__)
        self.ast = self.annotator.visit(self.ast)

    def testPointerAccess(self):
        """
a = PlacedInt8Array(100, 0x0)
a[3] = 42
        """
        assert self.ast.body[1].targets[0].typ == Int8
        assert self.ast.body[0].scope.find_symbol("a").typ == Pointer(Int8)


class TestFailingTypeAnnotation:
    def testUnknownSymbol(self):
        annotator = TypeAnnotator()
        an_ast = ast.parse("a = b")

        with pytest.raises(KeyError):
            an_ast = annotator.visit(an_ast)

    def testIllegalAssignmentToArrayElement(self):
        annotator = TypeAnnotator(hpcs_builtins.create_builtin_scope())
        an_ast = ast.parse("""
a = PlacedInt8Array(100, 0x0)
a[3] = "SomeString"
        """)

        with pytest.raises(TypeError):
            an_ast = annotator.visit(an_ast)
