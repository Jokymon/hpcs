import ast
from llvm import *
from llvm.core import *


ty_int = Type.int()
ty_func = Type.function(ty_int, [])


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


class CompilerVisitor(ast.NodeVisitor):
    def __init__(self):
        # TODO: change output stream
        self.temporary_stack = []
        self.temporary_index = 1

    def get_temporary(self):
        name = "%%temp%u" % self.temporary_index
        self.temporary_index += 1
        return name

    def visit_Module(self, node):
        self.module = Module.new('main')
        fun = self.module.add_function(ty_func, "main")
        self.bb = fun.append_basic_block("entry")
        self.builder = Builder.new(self.bb)
        #print("define i32 @main() {")
        for stmt in node.body:
            self.visit(stmt)
        #print("    ret i32 0")
        #print("}")
        print(self.module)

    def visit_FunctionDef(self, node):
        #print("args: ", node.args.args)
        #print(".function %s" % node.name)
        # name, args, annotation, arg*, vararg, ...... body
        pass

    def visit_Assign(self, node):
        temp = self.get_temporary()
        self.temporary_stack.append(temp)
        self.visit(node.value)
        #if node.targets[0].id=="a":
        #    print("    %a = alloca i32")
        #    print("    %temp1 = add i32 0, 3")
        #else:
        #    print("    %b = alloca i32")
        #    print("    %temp2 = add i32 0, 32")
        #print("    store i32 %s, i32* %%%s" % (temp, node.targets[0].id))

    def visit_BinOp(self, node):
        pass
        # left, op, right

    def visit_Name(self, node):
        pass
        #print(node)



