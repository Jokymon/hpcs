import ast
import sys
import annotators
import llvm_builder
import compiler
import hpcs_builtins


def main(file_name):
    with open(file_name) as source_file:
        source = ast.parse(source_file.read())
        checker = compiler.ConstraintChecker()
        checker.visit(source)
        type_annotator = annotators.TypeAnnotator(
            hpcs_builtins.create_builtin_scope())
        source = type_annotator.visit(source)
        vst = compiler.CompilerVisitor(llvm_builder.LLVMBuilder())
        vst.visit(source)

if __name__ == "__main__":
    main(sys.argv[1])
