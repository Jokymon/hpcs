import ast
import compiler
import annotators
import typing
import hpcs_builtins


class BuilderSpy:
    def __init__(self):
        self.actions = []

    def get_actions(self):
        return self.actions

    def assert_actions(self, action_list):
        assert self.actions == action_list

    def new_module(self, *args, **kwargs):
        return self

    def new_struct(self, name, struct):
        self.actions.append("STRUCT: %s %s" % (name, struct))
        return self

    def new_function(self, name, func_type):
        self.actions.append("FUNCTION: %s" % name)
        return self

    def add_basic_block(self, *args, **kwargs):
        return self

    def get_irbuilder(self, *args, **kwargs):
        return self

    def alloca(self, alloca_type, name):
        self.actions.append("ALLOCA: %s (%s)" % (name, alloca_type))
        return "'%s'" % name

    def store(self, value, alloca):
        self.actions.append("STORE: %s -> %s" % (value, alloca))

    def load(self, alloca, name):
        self.actions.append("LOAD: %s -> %s" % (alloca, name))

    def sext(self, value, ext_type, name):
        pass

    def inttoptr(self, value, target_type):
        self.actions.append("INTTOPTR: %u -> %s" % (value, target_type))

    def add(self, *args, **kwargs):
        pass

    def new_constant(self, const_type, value):
        self.actions.append("NEW_CONST: %s (%s)" % (value, const_type))
        return value

    def ret_void(self, *args, **kwargs):
        pass

    def verify(self, *args, **kwargs):
        pass


class TestByNewMethod:
    def setup_method(self, method):
        tree = ast.parse(method.__doc__)
        tree = annotators.TypeAnnotator().visit(tree)
        self.tree = tree
        self.builder_spy = BuilderSpy()
        self.compiler = compiler.CompilerVisitor(self.builder_spy)

    def testEmptyModule(self):
        """
# This is just an empty python module
        """
        self.compiler.visit(self.tree)
        self.builder_spy.assert_actions([
            "FUNCTION: main"])

    def testAssignSingleInteger(self):
        """
a = 2
        """
        self.compiler.visit(self.tree)
        self.builder_spy.assert_actions([
            "FUNCTION: main",
            "ALLOCA: a (Int8)",
            "NEW_CONST: 2 (Int8)",
            "STORE: 2 -> 'a'"])

    def testAssignSimpleExpression(self):
        """
a = 2 + 6
        """
        self.compiler.visit(self.tree)
        self.builder_spy.assert_actions([
            "FUNCTION: main",
            "ALLOCA: a (Int8)",
            "NEW_CONST: 2 (Int8)",
            "NEW_CONST: 6 (Int8)",
            "STORE: None -> 'a'"])

    def testEmptyClass(self):
        """
class AClass:
    pass
        """
        self.compiler.visit(self.tree)
        self.builder_spy.assert_actions([
            "FUNCTION: main",
            "STRUCT: AClass {  }"])


class TestBuiltins:
    def setup_method(self, method):
        tree = ast.parse(method.__doc__)
        tree = annotators.TypeAnnotator(
            hpcs_builtins.create_builtin_scope()).visit(tree)
        self.tree = tree
        self.builder_spy = BuilderSpy()
        self.compiler = compiler.CompilerVisitor(self.builder_spy)

    def testPlacedArray(self):
        """
a = PlacedInt8Array(100, 0x1000)
        """
        self.compiler.visit(self.tree)
        assert self.tree.body[0].scope.find_symbol("a").typ == \
            typing.Pointer(typing.Int8)
        self.builder_spy.assert_actions([
            "FUNCTION: main",
            "ALLOCA: a (ptr(Int8))",
            "NEW_CONST: 100 (Int8)",
            "NEW_CONST: 4096 (Int16)",
            "INTTOPTR: 4096 -> ptr(Int8)",
            "STORE: None -> 'a'"
            ])
