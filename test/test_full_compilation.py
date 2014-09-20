import pytest
from hpcs import compile_source


class TestFullLLVMCompilation:
    def testTestInput1(self):
        compile_source("test_input/test1.py")

    @pytest.mark.skipif(True, reason="Test2 still needs some rework")
    def testTestInput2(self):
        compile_source("test_input/test2.py")
