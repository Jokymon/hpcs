import ast
import sys
import annotators
import llvm_builder
import compiler


def main(file_name):
    with open(file_name) as source_file:
        source = ast.parse(source_file.read())
        checker = compiler.ConstraintChecker()
        checker.visit(source)
        source = annotators.TypeAnnotator().visit(source)
        vst = compiler.CompilerVisitor(llvm_builder.LLVMBuilder())
        vst.visit(source)
        #print(ast.dump(a))

if __name__=="__main__":
    main(sys.argv[1])
