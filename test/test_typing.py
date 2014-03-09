import pytest
import ast
from typing import *


class TestTypeEquality:
    def testVoidEquality(self):
        v1 = Void()
        v2 = Void()

        assert v1 == v2
        assert v1 == v1

    def testVoidInequality(self):
        v = Void()

        assert v != Int8
        assert v != Int16

    def testIntegerEquality(self):
        i8 = Int8
        i16 = Int16
        i32 = Int32

        assert i8 == Int8
        assert Int8 == Int8
        assert i16 == Int16

        assert Int8 != Int16

    def testSimpleFunctionEquality(self):
        func1 = Function(Void(), [])
        func2 = Function(Void(), [])

        assert func1 == func2

    def testSimpleFunctionInequality(self):
        func1 = Function(Void(), [])
        func2 = Function(Int8, [])
        func3 = Function(Void(), [Int8, Int8])

        assert func1 != Void()
        assert func2 != Int8

        assert func1 != func2
        assert func2 != func3
        assert func3 != func1


@pytest.fixture
def typesystem():
    return TypingSystem(None)


class TestTypeGeneration:
    def testInt8(self, typesystem):
        assert typesystem.get_type_from_number(8) == Int8
        assert typesystem.get_type_from_number(255) == Int8

    def testInt16(self, typesystem):
        assert typesystem.get_type_from_number(256) == Int16
        assert typesystem.get_type_from_number(65535) == Int16

    def testInt32(self, typesystem):
        assert typesystem.get_type_from_number(65536) == Int32


class TestTypeGenerationById:
    def testInt(self, typesystem):
        assert typesystem.get_type_for_id("Int8") == Int8
        assert typesystem.get_type_for_id("Int16") == Int16
        assert typesystem.get_type_for_id("Int32") == Int32

    def testUnknownType(self, typesystem):
        assert typesystem.get_type_for_id("some_unknown_id") is None


class TestTypeResolution:
    def testInt8Adding(self, typesystem):
        assert typesystem.resolve_types(Int8, Int8, ast.Add) == Int8

    def testInt8Int16Adding(self, typesystem):
        assert typesystem.resolve_types(Int8, Int16, ast.Add) == Int16

    def testInt16Int8Adding(self, typesystem):
        assert typesystem.resolve_types(Int16, Int8, ast.Add) == Int16
