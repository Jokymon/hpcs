import pytest
import mock
import ast
import compiler
import annotators
import typing
import llvm_builder


class CompilerTestBase:
    def setup_method(self, method):
        self.builder_mock = mock.Mock(llvm_builder.LLVMBuilder)
        self.module_mock = mock.Mock(llvm_builder.LLVMModule)
        self.function_mock = mock.Mock(llvm_builder.LLVMFunction)

        self.builder_mock.new_module.return_value = self.module_mock
        self.module_mock.new_function.return_value = self.function_mock

        tree = ast.parse(method.__doc__)
        tree = annotators.TypeAnnotator().visit(tree)
        self.tree = tree
        self.compiler = compiler.CompilerVisitor(self.builder_mock)


class TestAssignment(CompilerTestBase):
    def testEmptyModule(self):
        """
# This is just an empty python module
        """
        self.compiler.visit(self.tree)

        self.builder_mock.new_module.assert_called_with("main")
        self.module_mock.new_function.assert_called_with(
            "main",
            typing.Function(typing.Void(), []))

    def notestAssignSingleInter(self):
        """
a = 2
        """
        pass
