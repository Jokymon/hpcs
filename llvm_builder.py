import llvmlite.ir as ll
import llvmlite.binding as llvm
import typing


llvm.initialize()
llvm.initialize_native_asmprinter()
llvm.initialize_native_target()

compare_signed_int = {
    'EQ': '==',
    'NEQ': '!=',
    'LT': '<',
    'LTE': '<=',
    'GT': '>',
    'GTE': '>='
}


def convert_type(generic_type):
    if isinstance(generic_type, typing.Void):
        return ll.VoidType()
    elif isinstance(generic_type, typing.Bool):
        return ll.IntType(1)
    elif isinstance(generic_type, typing.Integer):
        return ll.IntType(generic_type.width)
    elif isinstance(generic_type, typing.String):
        return ll.PointerType(ll.IntType(8))
    elif isinstance(generic_type, typing.Pointer):
        return ll.PointerType(convert_type(generic_type.pointee_type))
    elif isinstance(generic_type, typing.Function):
        return_type = convert_type(generic_type.return_type)
        signature = [convert_type(t) for t in generic_type.signature]
        return ll.FunctionType(return_type, signature)
    else:
        raise Exception("Couldn't convert this type: %s" % generic_type)


class LLVMIRBuilder:
    # TODO: Do we have to create a wrapper for alloca's as well?
    def __init__(self, llvm_basic_block):
        self.builder = ll.IRBuilder(llvm_basic_block.basic_block)

    def alloca(self, signature, name):
        return self.builder.alloca(convert_type(signature), name=name)

    def store(self, value, alloca):
        return self.builder.store(value, alloca)

    def load(self, alloca, name):
        return self.builder.load(alloca, name)

    def add(self, left, right, name):
        return self.builder.add(left, right, name)

    def mul(self, left, right, name):
        return self.builder.mul(left, right, name)

    def compare(self, left, right, operator, name):
        llvm_operator = compare_signed_int[operator]
        return self.builder.icmp_unsigned(llvm_operator, left, right, name=name)

    def sext(self, value, signature, name):
        return self.builder.sext(value, convert_type(signature), name)

    def inttoptr(self, value, target_type):
        return self.builder.inttoptr(value, convert_type(target_type))

    def gep(self, pointer, indices):
        return self.builder.gep(pointer, indices)

    def branch(self, block):
        return self.builder.branch(block.basic_block)

    def cbranch(self, if_value, then_blk, else_blk):
        return self.builder.cbranch(if_value,
                                    then_blk.basic_block,
                                    else_blk.basic_block)

    def ret_void(self):
        return self.builder.ret_void()


class LLVMBasicBlock:
    def __init__(self, llvm_basic_block):
        self.basic_block = llvm_basic_block


class LLVMFunction:
    def __init__(self, llvm_function):
        self.function = llvm_function

    def add_basic_block(self, name):
        basic_block = self.function.append_basic_block(name)
        return LLVMBasicBlock(basic_block)


class LLVMModule:
    def __init__(self, name):
        self.module = ll.Module(name=name)

    def new_function(self, name, signature):
        func_ty = convert_type(signature)
        func = ll.Function(self.module, func_ty, name=name)
        return LLVMFunction(func)

    def new_global_variable(self, name, value):
        variable = ll.GlobalVariable(self.module, value.type, name)
        variable.initializer = value
        return variable

    def verify(self):
        llvm.parse_assembly(str(self.module))

    def __str__(self):
        return str(self.module)


class LLVMBuilder:
    def __init__(self):
        pass

    def new_module(self, name):
        return LLVMModule(name)

    def new_irbuilder(self, llvm_basic_block):
        return LLVMIRBuilder(llvm_basic_block)

    def new_struct(self, name, struct):
        return Type.struct([], name=name)

    def new_constant(self, signature, value):
        if isinstance(signature, typing.String):
            return ll.Constant(ll.ArrayType(ll.IntType(8), len(value)), bytearray(value, "utf-8"))
        else:
            return ll.Constant(convert_type(signature), value)
