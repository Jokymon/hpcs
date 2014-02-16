import pytest
import ast
from typing import *


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


class TestTypeResolution:
    def testInt8Adding(self, typesystem):
        assert typesystem.resolve_types(Int8, Int8, ast.Add) == Int8

    def testInt8Int16Adding(self, typesystem):
        assert typesystem.resolve_types(Int8, Int16, ast.Add) == Int16
