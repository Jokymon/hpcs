class Void:
    def __eq__(self, other):
        if isinstance(other, Void):
            return True
        return False


class Integer:
    def __init__(self, bit_width):
        self.width = bit_width

    def __str__(self):
        return "Int%u" % self.width


Int8 = Integer(8)
Int16 = Integer(16)
Int32 = Integer(32)


class Function:
    def __init__(self, return_type, signature):
        self.return_type = return_type
        self.signature = signature

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        if other.return_type != self.return_type:
            return False
        if other.signature != self.signature:
            return False
        return True


class Struct:
    def __init__(self):
        self.type_list = []

    def add_field(self, typ):
        self.type_list.append(typ)

    def __str__(self):
        type_strs = map(str, self.type_list)
        return "{ %s }" % ", ".join(type_strs)


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

    def get_type_for_id(self, id):
        if id in ["Int8", "Int16", "Int32"]:
            return eval(id)
        return None

    def resolve_types(self, type1, type2, operation):
        assert type(type1) == type(type2)  # can only resolve same base types
        if type1.width > type2.width:
            return type1
        return type2
