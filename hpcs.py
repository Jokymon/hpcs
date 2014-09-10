import os.path
import ast
import annotators
import llvm_builder
import compiler
import hpcs_builtins
from optparse import OptionParser
from llvm.ee import *


def compile_source(source_file_name):
    checker = compiler.ConstraintChecker()

    with open(source_file_name) as source_file:
        source = ast.parse(source_file.read())
    checker.visit(source)
    type_annotator = annotators.TypeAnnotator(
        hpcs_builtins.create_builtin_scope())
    source = type_annotator.visit(source)
    vst = compiler.CompilerVisitor(llvm_builder.LLVMBuilder())
    root = vst.visit(source)
    return root.module.module


def main():
    parser = OptionParser()
    parser.add_option("-S",
                      action="store_true", dest="compile_only", default=False,
                      help="only compile but don't assemble the source")
    parser.add_option("-o", dest="output_filename",
                      help="name of the output file", metavar="FILE")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        print("No input file given")
        return
    file_name = args[0]

    module = compile_source(file_name)

    tm = TargetMachine.new()

    if options.output_filename == "" or options.output_filename is None:
        (filebasename, suffix) = os.path.splitext(file_name)
        if options.compile_only:
            options.output_filename = filebasename+".S"
        else:
                options.output_filename = filebasename+".o"

    with open(options.output_filename, "wb") as target_file:
        if options.compile_only:
            target_file.write(tm.emit_assembly(module).encode())
        else:
            target_file.write(tm.emit_object(module))


if __name__ == "__main__":
    main()
