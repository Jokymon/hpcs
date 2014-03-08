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
        self.basicblock_mock = mock.Mock(llvm_builder.LLVMBasicBlock)
        self.irbuilder_mock = mock.Mock(llvm_builder.LLVMIRBuilder)

        self.builder_mock.new_module.return_value = self.module_mock
        self.module_mock.new_function.return_value = self.function_mock
        self.function_mock.add_basic_block.return_value = self.basicblock_mock
        self.basicblock_mock.get_irbuilder.return_value = self.irbuilder_mock

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
        self.function_mock.add_basic_block.assert_called_with(
            "entry")

    def testAssignSingleInter(self):
        """
a = 2
        """
        self.compiler.visit(self.tree)

        self.irbuilder_mock.alloca.assert_called_with(
            typing.Int8, "a")
        self.builder_mock.new_constant.assert_called_with(
            typing.Int8, 2)
        self.irbuilder_mock.store.assert_called_with(
            self.builder_mock.new_constant.return_value,
            self.irbuilder_mock.alloca.return_value)
