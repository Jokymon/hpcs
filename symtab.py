class Symbol(object):
    def __init__(self, name, typ=None):
        self.name = name
        self.typ = typ

    def __str__(self):
        return "Symbol '%s': %s" % (self.name, self.typ)


class SymbolTable(object):
    def __init__(self, parent):
        self.parent = parent
        self.table = {}

    def find_symbol(self, name):
        if name in self.table:
            return self.table[name]
        elif self.parent is None:
            return None
        else:
            return self.parent.find_symbol(name)

    def add_symbol(self, sym):
        self.table[sym.name] = sym
