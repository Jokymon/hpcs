pip install wget
python -m wget http://repo.continuum.io/pkgs/free/win-64/llvm-3.3-0.tar.bz2
python scripts\untar.py llvm-3.3-0.tar.bz2
path=%PATH%;c:\src\hpcs\Library\bin
python -m wget http://repo.continuum.io/pkgs/free/win-64/llvmpy-0.12.7-py34_0.tar.bz2
python scripts\untar.py llvmpy-0.12.7-py34_0.tar.bz2
set PYTHONPATH=c:\src\hpcs\Lib\site-packages
