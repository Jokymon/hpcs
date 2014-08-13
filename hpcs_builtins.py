import typing
import symtab


def signature(ret_type, param_types):
    def inside_decorator(function):
        function._ret_type = ret_type
        function._param_types = param_types
        return function
    return inside_decorator


@signature(typing.Pointer(typing.Int32), [typing.Int32, typing.Int32])
def PlacedInt8Array(node):
    pass


def create_builtin_scope():
    builtin_scope = symtab.SymbolTable(None)
    t = typing.Function(typing.Pointer(typing.Int32), [typing.Int32, typing.Int32])
    placedInt8Array = symtab.Symbol("PlacedInt8Array", t)
    builtin_scope.add_symbol(placedInt8Array)

    return builtin_scope
