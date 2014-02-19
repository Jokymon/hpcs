import ast
from llvm import *
from llvm.core import *


ty_func = Type.function(Type.void(), [])


class ConstraintChecker(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        assert node.decorator_list == [], "Can't handle decorators"
        assert node.args.kwarg == None, "kwargs are not supported"
        assert node.args.vararg == None, "varargs are not supported"
        assert node.args.defaults == [], "defaults are not supported"
        self.visit(node.name)
        self.visit(node.args)
        for stmt in node.body:
            self.visit(stmt)
        for decorator in node.decorator_list:
            self.visit(decorator)
        if node.returns is not None:
            self.visit(node.returns)


class CompilerVisitor(ast.NodeTransformer):
    def __init__(self):
        # TODO: change output stream
        pass

    def visit_Module(self, node):
        self.module = Module.new('main')
        fun = self.module.add_function(ty_func, "main")
        self.bb = fun.append_basic_block("entry")
        self.builder = Builder.new(self.bb)

        for sym in node.scope.table.values():
            alloca = self.builder.alloca(sym.typ, sym.name)
            sym.alloca = alloca

        for stmt in node.body:
            self.visit(stmt)

        self.builder.ret_void()
        self.module.verify()
        print(self.module)
        return node

    def visit_FunctionDef(self, node):
        # name, args, annotation, arg*, vararg, ...... body
        return node

    def visit_Assign(self, node):
        lhs = node.targets[0].id
        self.visit(node.value)
        target = node.scope.find_symbol(lhs).alloca
        self.builder.store(node.value.llvm_value, node.scope.find_symbol(lhs).alloca)
        return node

    def visit_BinOp(self, node):
        # left, op, right
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        node.llvm_value = self.builder.add(node.left.llvm_value, node.right.llvm_value, 'addtmp')
        return node

    def visit_Name(self, node):
        # TODO: could use the expr_context of node to find out what to do (load, store, ...)
        sym = node.sym
        node.llvm_value = self.builder.load(sym.alloca, sym.name)
        return node

    def visit_Num(self, node):
        # TODO: calculate the right size for the constant
        # TODO: Also think about type extension
        node.llvm_value = Constant.int(Type.int(8), node.n)
        return node



