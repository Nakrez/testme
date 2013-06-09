% TestMe Documentation
% Baptiste COVOLATO
% June 08, 2013

Usage
=====

testme.py [-h] [--dir DIR] [-v] [-c CATEGORY [CATEGORY ...]] [-x] [-f] [-l]

If you don't specify any directory to run. Then `TestMe` will try to run in the
current directory
o-h, --help            show this help message and exit
  --dir DIR             The directory where you want to run testme
    -v, --verbose         TestMe will display extra informations
      -c CATEGORY [CATEGORY ...], --category CATEGORY [CATEGORY ...]
                              Select specific categories to run
                                -x, --extra-light-display
                                                        Only print summary of each run category
                                                          -f, --full-display    Print all tests result
                                                            -l, --light-display   Print only failed tests

- Options:

    * -h \--help

        Show the help message and exit
    * \--dir directory

        Specify a directory where `TestMe` has to run
    * -v \--verbose

        Verbose mode : `TestMe` will print some extra information while running
    * -c \--category CATEGORY [CATEGORY ...]

        Run only the specified categories
    * -x \--extra-light-display

        Only display summary of each categories
    * -f \--full-display

        Display all run tests
    * -l \--light-display

        Only display tests that failed

Configuration file
==================

When `TestMe` is running in a directory it will need a configuration file named
"testme.conf". This configuration file describes all categories that `TestMe`
has to test and how to test each one of them.

Category
--------

To specify a category you declared it in the configuration file between [].
For example category `info` will be declared as `[info]`.

You can have extra options to specify how `TestMe` has to run the category.
All options that have a default value can not be unspecified if the default
value is the one you desired.

WARNING : All files (input, stdin, stdout, stderr) related to a single test must
have the same base name (with different extension). If you do not do as
specified `TestMe` may fail to properly execute your tests.
For example an input file name `test.py` must have `test.in`, `test.out`,
`test.err` files (respectively stdin, stdout, stderr). If they are activated.
Extensions can also be modified.

### input options ###

These options allow you to run over input file for tests in the specified
category.

When enabled `TestMe` will iterate over the `input_dir` and run for every file
the command line and test the outputs. (See `Variables` section to see how to
indicate input file to the command_line).

WARNING: All your input files must have the same extension and located in
the same directory.

* `input (default = off)`

    Enable the input file process.

* `input_dir (default = ${TESTME_CATEGORY_DIR}/input)`

    The directory where all input files are located.

* `input_ext (default = inp)`

    The extension that all your input files have.

### stdin options ###

These options allow you put input content on the standard input of the command
line

WARNING: All your stdin files must have the same extension and located in the
same directory.

* `stdin (default = off)`

    Enable the standard input files

* `stdin_dir (default = ${TESTME_CATEGORY_DIR}/stdin)`

    The directory where all references output are located. These output must
    have the same base name than the input test file.

* `stdin_ext (default = in)`

    The extension that all your stdin files have.

### stdout options ###

These options allow you to test the output of your tests in the specified
category.

WARNING: All your output references files must have the same
extension and located in the same directory.

* `stdout (default = off)`

    Enable the check between the standard output of the test and a reference
    output

* `stdout_dir (default = ${TESTME_CATEGORY_DIR}/stdout)`

    The directory where all references output are located. These output must
    have the same base name than the input test file.

* `stdout_ext (default = out)`

    The extension that all your output references have.

### stderr options ###

WARNING: All your output error references files must have the same
extension and located in the same directory.

* `stderr (default = off)`

    Enable the check between the standard error of the test and a reference
    error

* `stderr_dir (default = ${TESTME_CATEGORY_DIR}/stderr)`

    The directory where all references error are located. These output must
    have the same base name than the input test file.

* `stderr_ext (default = err)`

    The extension that all your error output references have.

### Command line invocation ###

This variable is mandatory and does not have any default value

* `cmd_line`

    Specify how to invoke a test. You have access to the special variable
    `TESTME_RUNNING_INPUT` (See `Variables` section for more infos)
    The command must be expressed in shell like style. If you have many binary
    invocation separated by `;` or `|` or `&&` or `||` only the last one will
    be tested.

### Error code check ###

These variables allow you to enable and specify a return code that the command
line must produce.

* `check_code (default = off)`

    Enable the check of return code

* `error_code (default = 0)`

    The return code that command line must produce.

### Display options ###

These options allow you to customize output produced by `TestMe` will running
your tests.

* `display_ok_tests (default = true)`

    `TestMe` will display every test that runs correctly

* `diplay_ko_tests (default = true)`

    `TestMe` will display every test that fails

* `display_summary (default = true)`

    `TestMe` will display a summary of all test run/failed/passed

Variables
---------

With `TestMe` you can use few variables to get specific directories, the current
processed input, ...

Those variables are described above.

Variables in configuration file must be surrounded by \$\{\}. For example variable
`TESTME_TESTDIR` in configuration file must appear as `${TESTME_TESTDIR}`

* `TESTME_TESTDIR`

    The root directory where tests are located
* `TESTME_CATEGORY`

    The name of the current category (only available when specifying
    a category)
* `TESTME_CATEGORY_DIR`

    The root directory of the category (only available when specifying
    a category)
* `TESTME_RUNNING_INPUT`

    This variable will take the value of the input value read.

    This variable is only available with `cmd_line` option because this is the
    only place where you may need the current input treated for example to
    pass it a command line of a binary (See example configuration file section
    `python_input`)

Example
-------

The configuration file above show two categories.

The first one "python2" passed input in the standard input of script.py
and test the resulted standard output and the error code

The second one "python_input" run different python scripts and compare there
output

    [python2]

    stdout = true
    stdin = true
    stdout_dir = ${TESTME_CATEGORY_DIR}/pyout
    stdin_dir = ${TESTME_CATEGORY_DIR}/pyin
    cmd_line = /usr/bin/python2 ${TESTME_CATEGORY_DIR}/script.py
    check_code = true
    error_code = 0
    display_ok_tests = true
    diplay_ko_tests = true
    display_summary = true

    [python_input]

    stdout = true
    input = true
    stdout_dir = ${TESTME_CATEGORY_DIR}/pyout
    input_dir = ${TESTME_CATEGORY_DIR}/pyinput
    input_ext = py
    cmd_line = /usr/bin/python2 ${TESTME_RUNNING_INPUT}
    display_ok_tests = true
    diplay_ko_tests = true
    display_summary = true
