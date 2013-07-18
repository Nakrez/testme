#!env /usr/bin/python3

#Copyright (C) 2013 Baptiste COVOLATO <b.covolato@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import sys
import os
import re
import configparser
import filecmp
import argparse

class TestPrinter:
    def __init__(self):
        self.verbose = False
        self.summary_on = True

    def print_summary(self, category, good, total):
        if self.summary_on:
            print("[TESTME] Category : '" + category + "' :", good, "/", total)

    def print_verbose(self, message):
        if self.verbose:
            print(message)

    def print_error(self, message):
        print("\033[91m" + message + "\033[0m")

class TestSuit:
    def __init__(self, printer):
        self.environement = {}
        self.test_list = {}
        self.running_cat = ""
        self.running_dir = ""
        self.ext = ""
        self.total_test = 0
        self.total_good = 0
        self.cat_test = 0
        self.cat_good = 0
        self.printer = printer

    def expand(self, string):
        while 1:
            m = re.search('\$\{(.*?)\}', string)

            if m == None or self.environement.get(m.group(1), None) == None:
                break

            string = re.sub('\$\{' + m.group(1) + '\}', self.environement[m.group(1)], string)

        return string

    def cat_field_get(self, field):
        if isinstance(self.test_list[self.running_cat][field], str):
            return self.expand(self.test_list[self.running_cat][field])
        else:
            return self.test_list[self.running_cat][field]

    def is_runnable(self):
        if testme_args.get('category', None) != None:
            return testme_args['category'].count(self.running_cat) > 0

        return True

    def run_directory(self):
        try:
            for dir_file in os.listdir(self.cat_field_get(self.running_dir)):
                if dir_file.endswith(self.cat_field_get(self.ext)):
                    self.total_test += 1
                    self.cat_test += 1
                    test_result = self.run_test(category, files)
                    if test_result:
                        self.cat_good += 1
                        self.total_good += 1
                    self.printer.print_result(test_result, category, files)

            self.printer.print_summary(self.running_cat, self.total_test,
                                       self.cat_test)

        except OSError:
           self.printer.print_error("[TESTME] Fatal error with " +
                                    "directory : " +
                                    self.cat_field_get(self.running_dir))

    def run(self):
        self.total_test = 0
        self.total_good = 0

        # Run every categories
        for cat in self.test_list:
            self.cat_test = 0
            self.cat_good = 0
            self.running_cat = cat

            if not self.is_runnable():
                continue

            print("\n[TESTME] Running tests in", self.running_cat)
            self.running_dir = 'input_dir' if self.cat_field_get('input') else 'stdin_dir'
            self.ext = 'input_ext' if self.cat_field_get('input') else 'stdin_ext'

            self.run_directory()

        print("\n[TESTME] Final result :", self.total_good, "/", self.total_test)

testme_version = "0.2"
testme_config_name = "testme.conf"
testme_args = {}
testme_to_run = {}
testme_env = {}


def update_env(cat):
    global testme_env

    testme_env['TESTME_TESTDIR'] = testme_args['dir']
    testme_env['TESTME_CATEGORY'] = cat
    testme_env['TESTME_CATEGORY_DIR'] = os.path.join(testme_args['dir'], cat)

def change_extension(change_file, ext):
    path = os.path.splitext(change_file)
    return path[0] + "." + ext

def print_verbose(msg):
    if testme_args.get('verbose', None):
        print(msg)

def run(category, test_file):
    global testme_env

    command = ""
    ret_value = True

    if testme_to_run[category]['input']:
        full_path = os.path.join(testme_to_run[category]['input_dir'], test_file)
        testme_env['TESTME_RUNNING_INPUT'] = full_path

    if testme_to_run[category]['stdin'] and testme_to_run[category]['input']:
        stdin = change_extension(full_path, testme_to_run[category]['stdin_ext'])
        command = "cat " + stdin + " | "
    elif testme_to_run[category]['stdin']:
        full_path = os.path.join(testme_to_run[category]['stdin_dir'], test_file)
        command = "cat " + full_path + " | "

    command += parse_string(testme_to_run[category]['cmd_line'])

    if testme_to_run[category]['stdout']:
        command += " > /tmp/testme.stdout"
        stdout = change_extension(test_file, testme_to_run[category]['stdout_ext'])
        stdout = os.path.join(testme_to_run[category]['stdout_dir'], stdout)
    if testme_to_run[category]['stderr']:
        command += " > /tmp/testme.stderr"
        stderr = change_extension(test_file, testme_to_run[category]['stderr_ext'])
        stderr = os.path.join(testme_to_run[category]['stderr_dir'], stderr)

    command_exit = os.WEXITSTATUS(os.system(command))

    if testme_to_run[category]['stdout']:
        if os.path.exists(stdout):
            ret_value &= filecmp.cmp("/tmp/testme.stdout", stdout)
        else:
            print_verbose("\033[33m[TESTME] " + stdout + " not present stdout ignored\033[0m")
    if testme_to_run[category]['stderr']:
        if os.path.exists(stderr):
            ret_value &= filecmp.cmp("/tmp/testme.stdout", stderr)
        else:
            print_verbose("\033[33m[TESTME] " + stderr + " not present stderr ignored\033[0m")

    if testme_to_run[category]['check_code']:
        ret_value &= str(command_exit) in testme_to_run[category]['error_code']

    return ret_value

def print_result(test_result, category, file_name):
    if (test_result and (testme_to_run[category]['display_ok_tests']
                        or testme_args.get('full_display', False))
                   and not testme_args.get('extra_light_display', False)):
        print("\033[32m[TESTME] Test :", file_name, "passed\033[0m")
    elif (not test_result and (testme_to_run[category]['display_ko_tests']
                               or testme_args.get('full_display', False)
                               or testme_args.get('light_display', False))
                          and not testme_args.get('extra_light_display', False)):
        print("\033[91m[TESTME] Test :", file_name, "failed\033[0m")


def die_on_error(msg):
    sys.stderr.write("[TESTME][ERROR] " + msg + "\n")
    sys.exit(1)


class ConfigBuilder:
    def __init__(self, printer, filename):
        self.filename = filename
        self.configuration = {}
        self.printer = printer

    def default(self, cat_name):
        return {'stdout' : 0, # Stdout test
                'stdin' : 0, # Stdin test
                'stderr' : 0, # Stderr test
                'input' : 0, # Input test
                'input_dir' : os.path.join(testme_args['dir'], cat_name, "input"),
                'stdout_dir' : os.path.join(testme_args['dir'], cat_name, "stdout"),
                'stdin_dir' : os.path.join(testme_args['dir'], cat_name, "stdin"),
                'stderr_dir' : os.path.join(testme_args['dir'], cat_name, "stderr"),
                'input_ext' : 'inp',
                'stdout_ext' : 'out',
                'stdin_ext' : 'in',
                'stderr_ext' : 'err',
                'cmd_line' : '',
                'check_code' : 0,
                'error_code' : ["0"],
                'display_ok_tests' : 1,
                'display_ko_tests' : 1,
                'display_summary' : 1}

    def get_bool(self, section, value):
        try:
            self.configuration[section][value] = self.parser.getboolean(section,
                                                                        value)
        except configparser.NoOptionError:
            return 0
        except:
            die_on_error(value + " in section '" + section + "' is not a boolean")

    def get_string(self, section, value):
        try:
            self.configuration[section][value] = self.parser.get(section, value)
            return
        except configparser.NoOptionError:
            return

    def get_int(self, section, value):
        try:
            self.configuration[section][value] = self.parser.getint(section, value)
        except configparser.NoOptionError:
            return 0
        except:
            die_on_error(value + " in section '" + section + "' is not an integer")

    def parse_config(self):
        self.parser = configparser.RawConfigParser()
        self.parser.read(self.filename)

        for section in self.parser.sections():
            self.configuration[section] = self.default(section)

            self.get_bool(section, 'stdout')
            self.get_bool(section, 'stdin')
            self.get_bool(section, 'stderr')
            self.get_bool(section, 'input')
            self.get_string(section, 'stdout_dir')
            self.get_string(section, 'stdin_dir')
            self.get_string(section, 'stderr_dir')
            self.get_string(section, 'input_dir')
            self.get_string(section, 'cmd_line')
            self.get_string(section, 'input_ext')
            self.get_string(section, 'stdin_ext')
            self.get_string(section, 'stdout_ext')
            self.get_string(section, 'stderr_ext')
            self.get_string(section, 'cmd_line')
            self.get_bool(section, 'check_code')
            self.get_string(section, 'error_code')
            self.get_bool(section, 'display_ok_tests')
            self.get_bool(section, 'diplay_ko_tests')
            self.get_bool(section, 'display_summary')

            if self.configuration[section]['error_code'] is str:
                self.configuration[section]['error_code'] = self.configuration[section]['error_code'].split("|")

def parse_argv():
    global testme_args
    argc = 1

    if len (sys.argv) == 1:
        return # No option to parse

    parser = argparse.ArgumentParser(description='TestMe ' + testme_version
                                     + ' by Baptiste COVOLATO')

    parser.add_argument('--dir', action="store",
                        help='The directory where you want to run testme')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='TestMe will display extra informations')
    parser.add_argument('-c', '--category', nargs='+', action="store",
                        help='Select specific categories to run')
    parser.add_argument('-x', '--extra-light-display', action="store_true",
                        help='Only print summary of each run category')
    parser.add_argument('-f', '--full-display', action="store_true",
                        help='Print all tests result')
    parser.add_argument('-l', '--light-display', action="store_true",
                        help='Print only failed tests')

    testme_args = vars(parser.parse_args())

def main():
    printer = TestPrinter()
    parse_argv()

    printer.verbose = testme_args.get('verbose', None)

    if testme_args.get('dir', None) == None:
        testme_args['dir'] = os.getcwd()

    printer.print_verbose("[TESTME] Running directory : " + testme_args['dir'])
    config_full_path = os.path.join(testme_args['dir'], testme_config_name)

    config = ConfigBuilder(printer, config_full_path)
    config.parse_config()

    test_suit = TestSuit(printer)
    test_suit.test_list = config.configuration
    test_suit.run()

if __name__ == "__main__":
    main()
