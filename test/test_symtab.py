from symtab import *


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



