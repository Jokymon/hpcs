# TODO list for this module:
# - define and implement type coercion when types are not matching
# - What types do we use, Python types? special types so that we can mark out
#   8-bit, 16-bit, etc. numeric types? How can we then make sure that
#   operations work the same when run in Python and in the assembled version?
#   (e.g. 8-bit overflow)
# - How should be handle the pointer type?

import typing
import ast


class Symbol(object):
    def __init__(self, name, typ=None):
        self.name = name
        self.typ = typ


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


class TypeAnnotator(ast.NodeTransformer):
    def __init__(self):
        self.scope_stack = []
        self.push_scope()   # create outer-most scope
        self.typing = typing.TypingSystem(None)

    def push_scope(self):
        self.scope_stack.append({})

    def pop_scope(self):
        self.scope_stack.pop()

    def lookup_symbol(self, id):
        if not self.scope_stack:
            return None
        for scope in reversed(self.scope_stack):
            if id in scope.keys():
                return scope[id]
        return None

    def add_symbol_to_top_scope(self, symbol):
        self.scope_stack[-1][symbol.name] = symbol

    def visit_arguments(self, node):
        for arg in node.args:
            sym = Symbol(arg.arg)
            assert isinstance(arg.annotation, ast.Name), "Argument annotation must be a type identifier"
            # TODO: Yuk, this eval is ugly and evil, is there any other way?
            sym.typ = eval(arg.annotation.id)
            self.add_symbol_to_top_scope(sym)
        
        return node
    
    def visit_FunctionDef(self, node):
        self.push_scope()
        node.args = self.visit(node.args)
        node.body = [ self.visit(child) for child in node.body ]
        node.decorator_list = [ self.visit(node.decorator_list) for child in node.decorator_list ]
        # TODO: The return type of the function can also be determined using
        # the types of Return nodes
        if node.returns is not None:
            node.returns = self.visit(node.returns)
        else:
            node.returns = None
        self.pop_scope()

        return node

    def visit_Assign(self, node):
        # targets* = value (expr)
        node.value = self.visit(node.value)
        assert len(node.targets)==1, "Only single target is supported for assignments"
        sym = self.lookup_symbol(node.targets[0].id)
        if sym is None:
            sym = Symbol(node.targets[0].id)
            sym.typ = node.value.typ
            self.add_symbol_to_top_scope(sym)
        node.targets[0].typ = node.value.typ
        return node

    def visit_BinOp(self, node):
        node.left = self.visit(node.left)
        node.op = self.visit(node.op)
        node.right = self.visit(node.right)
        # TODO: handle more complicated cases such as int * string etc.
        node.typ = self.typing.resolve_types(node.left.typ, node.right.typ, node.op)
        return node

    def visit_Num(self, node):
        node.typ = self.typing.get_type_from_number(node.n)
        return node

    def visit_Name(self, node):
        if not hasattr(node, "typ"):
            sym = self.lookup_symbol(node.id)
            if hasattr(sym, "typ") and sym.typ is not None:
                node.typ = sym.typ
            else:
                raise KeyError("Can't determine type of '%s' @%u:%u" % (node.id, node.lineno, node.col_offset))
        return node
