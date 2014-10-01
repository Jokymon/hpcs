# TODO list for this module:
# - define and implement type coercion when types are not matching
# - What types do we use, Python types? special types so that we can mark out
#   8-bit, 16-bit, etc. numeric types? How can we then make sure that
#   operations work the same when run in Python and in the assembled version?
#   (e.g. 8-bit overflow)
# - How should be handle the pointer type?

import typing
import symtab
import ast
from errors import *


class TypeAnnotator(ast.NodeTransformer):
    def __init__(self, root_symbol_table=None):
        self.top_scope = symtab.SymbolTable(root_symbol_table)
        self.typing = typing.TypingSystem(None)

    def push_scope(self, scope):
        self.top_scope = scope

    def pop_scope(self):
        self.top_scope = self.top_scope.parent

    def lookup_symbol(self, id):
        return self.top_scope.find_symbol(id)

    def add_symbol_to_top_scope(self, symbol):
        self.top_scope.add_symbol(symbol)

    def visit_arguments(self, node):
        for arg in node.args:
            sym = symtab.Symbol(arg.arg)
            assert isinstance(arg.annotation, ast.Name), \
                "Argument annotation must be a type identifier"
            sym.typ = self.typing.get_type_for_id(arg.annotation.id)
            self.add_symbol_to_top_scope(sym)

        return node

    def visit_Module(self, node):
        scope = symtab.SymbolTable(self.top_scope)
        node.scope = scope
        self.push_scope(scope)
        node.body = [self.visit(stmt) for stmt in node.body]
        self.pop_scope()
        return node

    def visit_FunctionDef(self, node):
        function_scope = symtab.SymbolTable(self.top_scope)
        self.push_scope(function_scope)
        node.scope = function_scope

        node.args = self.visit(node.args)
        # TODO: The return type of the function can also be determined using
        # the types of Return nodes
        return_type = None
        if node.returns is not None:
            assert isinstance(node.returns, ast.Name), \
                "Return annotation must be a type identifier"
            return_type = self.typing.get_type_for_id(node.returns.id)
        sym = symtab.Symbol(node.name)
        sym.typ = typing.Function(return_type, node.args)
        # TODO: The following line is a really ugly access of above scope; but
        # is needed since for the body and the arguments we need to be inside
        # the function scope
        self.top_scope.parent.add_symbol(sym)
        node.body = [self.visit(child) for child in node.body]
        node.decorator_list = [self.visit(node.decorator_list)
                               for child in node.decorator_list]
        self.pop_scope()

        return node

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise CompilationError(
                "Call of a function must be done through an explicit name",
                "<file>", node.lineno, node.col_offset)
        sym = self.lookup_symbol(node.func.id)
        if not isinstance(sym.typ, typing.Function):
            raise CompilationError("Can't call non-function symbol '%s'" %
                                   sym.name, "<file>", node.lineno,
                                   node.col_offset)
        node.args = [self.visit(arg) for arg in node.args]
        node.typ = sym.typ.return_type
        node.scope = self.top_scope
        return node

    def visit_Assign(self, node):
        # targets* = value (expr)
        node.scope = self.top_scope
        node.value = self.visit(node.value)
        if not hasattr(node.value, "typ"):
            raise KeyError("Can't determine type of '%s' @%u:%u" %
                           (node.value.id,
                            node.value.lineno, node.value.col_offset))
        node.targets = [self.visit(target) for target in node.targets]
        target = node.targets[0]
        if isinstance(target, ast.Name):
            sym = self.lookup_symbol(node.targets[0].id)
            if sym is None:
                sym = symtab.Symbol(node.targets[0].id)
                sym.typ = node.value.typ
                self.add_symbol_to_top_scope(sym)
            node.targets[0].typ = node.value.typ
        elif isinstance(target, ast.Subscript):
            if target.typ != node.value.typ:
                raise TypeError("Cannot assign %s to %s @%u:%u" %
                                (node.value.typ, target.typ,
                                 node.lineno, node.col_offset))
        return node

    def visit_BinOp(self, node):
        node.left = self.visit(node.left)
        node.op = self.visit(node.op)
        node.right = self.visit(node.right)
        # TODO: handle more complicated cases such as int * string etc.
        node.typ = self.typing.resolve_types(
            node.left.typ,
            node.right.typ,
            node.op)
        return node

    def visit_Compare(self, node):
        node.left = self.visit(node.left)
        node.ops = [self.visit(op) for op in node.ops]
        node.comparators = [self.visit(comp) for comp in node.comparators]
        node.typ = typing.Bool()
        return node

    def visit_Subscript(self, node):
        # value, slice, ctx
        node.value = self.visit(node.value)
        node.slice = self.visit(node.slice)
        if not isinstance(node.value.typ, typing.Pointer):
            raise TypeError(
                "Expecting a pointer value. Can't dereference value @%u:%u" %
                (node.lineno, node.col_offset))
        node.typ = node.value.typ.pointee_type
        return node

    def visit_Num(self, node):
        node.typ = self.typing.get_type_from_number(node.n)
        return node

    def visit_Str(self, node):
        node.typ = typing.String()
        return node

    def visit_Name(self, node):
        if not hasattr(node, "typ"):
            sym = self.lookup_symbol(node.id)
            if hasattr(sym, "typ") and sym.typ is not None:
                node.typ = sym.typ
            node.sym = sym
        return node
