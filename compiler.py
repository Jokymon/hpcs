import ast
import llvm_builder
from typing import *


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
        fun = module.new_function("main", Function(Void(), []))
        self.bb = fun.add_basic_block("entry")
        self.builder = self.code_builder.new_irbuilder(self.bb)

        for sym in node.scope.table.values():
            alloca = self.builder.alloca(sym.typ, sym.name)
            sym.alloca = alloca

        for stmt in node.body:
            self.visit(stmt)

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
        return node

    def visit_Assign(self, node):
        lhs = node.targets[0].id
        self.visit(node.value)
        target = node.scope.find_symbol(lhs).alloca
        self.builder.store(node.value.llvm_value,
                           node.scope.find_symbol(lhs).alloca)
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
        node.llvm_value = self.builder.add(left, right, 'addtmp')
        return node

    def visit_Name(self, node):
        # TODO: could use the expr_context of node to find out what to do
        # (load, store, ...)
        sym = node.sym
        node.llvm_value = self.builder.load(sym.alloca, sym.name)
        return node

    def visit_Num(self, node):
        node.llvm_value = self.code_builder.new_constant(node.typ, node.n)
        return node
