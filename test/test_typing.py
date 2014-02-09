import pytest
import ast
from typing import *


@pytest.fixture
def typesystem():
    return TypingSystem(None)


class TestTypeGeneration:
    def testUInt8(self, typesystem):
        assert typesystem.get_type_from_number(8) == UInt8
        assert typesystem.get_type_from_number(255) == UInt8

    def testUInt16(self, typesystem):
        assert typesystem.get_type_from_number(256) == UInt16
        assert typesystem.get_type_from_number(65535) == UInt16

    def testUInt32(self, typesystem):
        assert typesystem.get_type_from_number(65536) == UInt32


class TestTypeResolution:
    def testUInt8Adding(self, typesystem):
        assert typesystem.resolve_types(UInt8, UInt8, ast.Add) == UInt8

    def testUInt8UInt16Adding(self, typesystem):
        assert typesystem.resolve_types(UInt8, UInt16, ast.Add) == UInt16
