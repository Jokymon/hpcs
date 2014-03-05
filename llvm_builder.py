from llvm.core import *


class LLVMModule:
    def __init__(self, name):
        pass


class LLVMBuilder:
    def __init__(self):
        pass

    def new_module(self, name):
        module = Module.new(name)
        return module

