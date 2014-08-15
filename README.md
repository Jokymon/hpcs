hpcs
====

Hirvi Python Compiler Suite

Getting started
---------------

This project only works with Python >= 3.0 since it makes heavy use of
annotations. The prerequisites for this project are defined in the
requirements.txt file. You can simply install them using `pip` with the
following line:

    pip install -r requirements.txt

However under Windows things are little more difficult since the `llvmpy`
package cannot be installed as simply as under Linux. However you can use the
scripts in `scripts` folders like this. Make sure `pip` is in the `PATH`.

    scripts\prepare_win.bat

After that you have tell Python where the newly installed library can be found
by running the following script. This script has to be run on every new command
shell on which you want to do HPCS development.

    scripts\hpcs_vars.bat
