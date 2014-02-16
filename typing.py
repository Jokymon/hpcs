from llvm.core import *


Int8 = Type.int(8)
Int16 = Type.int(16)
Int32 = Type.int(32)


class TypingSystem(object):
    def __init__(self, platform):
        self.platform = platform

    def get_type_from_number(self, value):
        if value < 2**8:
            return Int8
        elif value < 2**16:
            return Int16
        else:
            return Int32

    def resolve_types(self, type1, type2, operation):
        assert type(type1)==type(type2) # can only resolve same base types
        if type1.width > type2.width:
            return type1
        return type2
