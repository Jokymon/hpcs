class BaseType(object):
    pass


class NumericType(type):
    def __lt__(cls, other):
        return cls.size_in_bits < other.size_in_bits


class UInt8(metaclass=NumericType):
    size_in_bits = 8


class UInt16(metaclass=NumericType):
    size_in_bits = 16


class UInt32(metaclass=NumericType):
    size_in_bits = 32


class TypingSystem(object):
    def __init__(self, platform):
        self.platform = platform

    def get_type_from_number(self, value):
        if value < 2**8:
            return UInt8
        elif value < 2**16:
            return UInt16
        else:
            return UInt32

    def resolve_types(self, type1, type2, operation):
        return max(type1, type2)
