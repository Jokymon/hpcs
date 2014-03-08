from llvm.core import *
import typing


def convert_type(generic_type):
    if isinstance(generic_type, typing.Void):
        return Type.void()
    elif isinstance(generic_type, typing.Integer):
        return Type.int(generic_type.width)
    elif isinstance(generic_type, typing.Function):
        return_type = convert_type(generic_type.return_type)
        signature = [ convert_type(t) for t in generic_type.signature ]
        return Type.function(return_type, signature)
    else:
        raise Exception("Couldn't convert this type: %s" % generic_type)


class LLVMIRBuilder:
    # TODO: Do we have to create a wrapper for alloca's as well?
    def __init__(self, llvm_ir_builder):
        self.builder = llvm_ir_builder

    def alloca(self, signature, name):
        return self.builder.alloca(convert_type(signature), name)

    def store(self, value, alloca):
        return self.builder.store(value, alloca)

    def load(self, alloca, name):
        return self.builder.load(alloca, name)

    def add(self, left, right, name):
        return self.builder.add(left, right, name)

    def sext(self, value, signature, name):
        return self.builder.sext(value, convert_type(signature), name)

    def ret_void(self):
        return self.builder.ret_void()


class LLVMBasicBlock:
    def __init__(self, llvm_basic_block):
        self.basic_block = llvm_basic_block

    def get_irbuilder(self):
        builder = Builder.new(self.basic_block)
        return LLVMIRBuilder(builder)
        #return Builder.new(self.basic_block)


class LLVMFunction:
    def __init__(self, llvm_function):
        self.function = llvm_function

    def add_basic_block(self, name):
        basic_block = self.function.append_basic_block(name)
        return LLVMBasicBlock(basic_block)


class LLVMModule:
    def __init__(self, name):
        self.module = Module.new(name)

    def new_function(self, name, signature):
        func = self.module.add_function(convert_type(signature), name)
        return LLVMFunction(func)

    def verify(self):
        self.module.verify()

    def __str__(self):
        return str(self.module)


class LLVMBuilder:
    def __init__(self):
        pass

    def new_module(self, name):
        return LLVMModule(name)

    def new_constant(self, signature, value):
        # TODO: use the right function of Constant based on signature
        return Constant.int(convert_type(signature), value)

