import ast
import annotators
import llvm_builder
from typing import *


compare_op = {
    ast.Eq: 'EQ',
    ast.NotEq: 'NEQ',
    ast.Lt: 'LT',
    ast.LtE: 'LTE',
    ast.Gt: 'GT',
    ast.GtE: 'GTE',
}


class ConstraintChecker(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        assert node.decorator_list == [], "Can't handle decorators"
        assert node.args.kwarg is None, "kwargs are not supported"
        assert node.args.vararg is None, "varargs are not supported"
        assert node.args.defaults == [], "defaults are not supported"
        self.visit(node.args)
        for stmt in node.body:
            self.visit(stmt)
        for decorator in node.decorator_list:
            self.visit(decorator)
        if node.returns is not None:
            self.visit(node.returns)

    def visit_Assign(self, node):
        self.visit(node.value)
        for target in node.targets:
            self.visit(target)
        assert len(node.targets) == 1, \
            "Only single target is supported for assignments"


class CompilerVisitor(ast.NodeTransformer):
    def __init__(self, code_builder):
        # TODO: change output stream
        self.code_builder = code_builder

    def visit_Module(self, node):
        module = self.code_builder.new_module('main')
        self.module = module
        self.fun = module.new_function("main", Function(Void(), []))
        bb = self.fun.add_basic_block("entry")
        self.builder = self.code_builder.new_irbuilder(bb)
        self.in_main = True

        for sym in node.scope.table.values():
            if not isinstance(sym.typ, Function):
                alloca = self.builder.alloca(sym.typ, sym.name)
                sym.alloca = alloca

        for stmt in node.body:
            self.visit(stmt)

        if self.in_main:
            self.builder.ret_void()
        module.verify()
        node.module = module
        return node

    def visit_ClassDef(self, node):
        # identifier name, expr* bases, stmt* body, expr* decorator_list
        struct = self.code_builder.new_struct(node.name, Struct())
        return node

    def visit_FunctionDef(self, node):
        # name, args, annotation, arg*, vararg, ...... body
        if self.in_main:
            self.builder.ret_void()
            self.in_main = False

        self.fun = self.module.new_function(node.name, Function(Void(), []))
        bb = self.fun.add_basic_block("entry")
        self.builder = self.code_builder.new_irbuilder(bb)

        for sym in node.scope.table.values():
            if not isinstance(sym.typ, Function):
                alloca = self.builder.alloca(sym.typ, sym.name)
                sym.alloca = alloca

        node.body = [self.visit(stmt) for stmt in node.body]

        self.builder.ret_void()
        return node

    def visit_While(self, node):
        # test, body, orelse
        while_condition_block = self.fun.add_basic_block("while_condition")
        while_statement_block = self.fun.add_basic_block("while_statements")
        after_while_block = self.fun.add_basic_block("after_while_block")

        self.builder.branch(while_condition_block)

        self.builder = self.code_builder.new_irbuilder(while_condition_block)
        node.test = self.visit(node.test)
        self.builder.cbranch(node.test.llvm_value,
                             while_statement_block,
                             after_while_block)

        self.builder = self.code_builder.new_irbuilder(while_statement_block)
        node.body = [self.visit(stmt) for stmt in node.body]
        self.builder.branch(while_condition_block)

        self.builder = self.code_builder.new_irbuilder(after_while_block)

        return node

    def visit_Assign(self, node):
        node.targets = [self.visit(target) for target in node.targets]
        node.value = self.visit(node.value)
        self.builder.store(node.value.llvm_value,
                           node.targets[0].llvm_value)
        return node

    def visit_Call(self, node):
        function_name = node.func.id
        function = node.scope.find_symbol(function_name)
        if hasattr(function, "generator"):
            return function.generator(self, node, self.builder)
        else:
            return node

    def visit_BinOp(self, node):
        # left, op, right
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        left = node.left.llvm_value
        right = node.right.llvm_value
        if node.left.typ.width > node.right.typ.width:
            right = self.builder.sext(right, node.left.typ, 'right_extended')
        elif node.right.typ.width > node.left.typ.width:
            left = self.builder.sext(left, node.right.typ, 'left_extended')
        if isinstance(node.op, ast.Add):
            node.llvm_value = self.builder.add(left, right, 'addtmp')
        elif isinstance(node.op, ast.Mult):
            node.llvm_value = self.builder.mul(left, right, 'multmp')
        return node

    def visit_Compare(self, node):
        # left, ops*, comparators*
        node.left = self.visit(node.left)
        node.ops = [self.visit(op) for op in node.ops]
        node.comparators = [self.visit(comp) for comp in node.comparators]

        # TODO: We currently only handle one single comparator
        left = node.left.llvm_value
        right = node.comparators[0].llvm_value
        if node.left.typ.width > node.comparators[0].typ.width:
            right = self.builder.sext(right, node.left.typ, 'right_extended')
        elif node.comparators[0].typ.width > node.left.typ.width:
            left = self.builder.sext(left, node.comparators[0].typ,
                                     'left_extended')
        operator = compare_op[node.ops[0].__class__]
        node.llvm_value = self.builder.compare(left, right, operator,
                                               'comptmp')
        return node

    def visit_Index(self, node):
        node.value = self.visit(node.value)
        node.llvm_value = node.value.llvm_value
        return node

    def visit_Subscript(self, node):
        # value, slice, ctx
        node.value = self.visit(node.value)
        node.slice = self.visit(node.slice)
        idx = self.builder.gep(node.value.llvm_value, [node.slice.llvm_value])
        node.llvm_value = self.builder.load(idx, 'subscript')
        return node

    def visit_Name(self, node):
        if node.loading_context==annotators.ValueContext:
            sym = node.sym
            node.llvm_value = self.builder.load(sym.alloca, sym.name)
        elif node.loading_context==annotators.AddressContext:
            node.llvm_value = node.sym.alloca
        return node

    def visit_Num(self, node):
        node.llvm_value = self.code_builder.new_constant(node.typ, node.n)
        return node

    def visit_Str(self, node):
        constant = self.code_builder.new_constant(node.typ, node.s)
        var = self.module.new_global_variable("string_constant", constant)
        value = self.builder.gep(var, 
                                 2*[self.code_builder.new_constant(Int32, 0)])

        node.llvm_value = value
        return node
