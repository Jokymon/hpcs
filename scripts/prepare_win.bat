pip install wget
python -m wget http://repo.continuum.io/pkgs/free/win-64/llvm-3.2-0.tar.bz2
python scripts\untar.py llvm-3.2-0.tar.bz2
path=%PATH%;c:\src\hpcs\Library\bin
python -m wget http://repo.continuum.io/pkgs/free/win-64/llvmpy-0.12.6-py34_0.tar.bz2
python scripts\untar.py llvmpy-0.12.6-py34_0.tar.bz2
