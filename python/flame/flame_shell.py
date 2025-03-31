# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# Interactive flame shell
#


import cmd
import sys

from flame.license_db import FossLicenses
from flame.format import OutputFormatterFactory


class FlameShell(cmd.Cmd):
#    intro = 'Welcome to the Flame shell. Type help or ? to list commands.\n'
    prompt = '>>> '
    file = None

    def __init__(self, verbose=False):
        cmd.Cmd.__init__(self)
        if verbose:
            self.do_verbose(None)
            self.output('Welcome to the Flame shell. Type help or ? to list commands.\n')
        else:
            self.do_silent(None)
        self.formatter = None
        self.flame = FossLicenses()

    def output(self, string, end="\n"):
        print(string, end=end)

    def verbose(self, string, end="\n"):
        if self.verbose_mode:
            print(string, end=end)

    def __handle_error(self, error):
        print(str(error))

    def do_exit(self, arg):
        """Exit the interactive shell"""
        return True

    def do_EOF(self, args):
        """Sending EOF (e.g. Control-d) will exit the interactive shell"""
        return True

    def emptyline(self):
        return ""

    def __read_license(self):
        if self.verbose_mode:
            print("Enter license name: ", end="")
        try:
            line = input()
            return line
        except EOFError:
            pass

    
    def do_unknown(self, arg):
        """."""
        license_name = self.__read_license()
        try:
            unknowns = self.flame.unknown_symbols([license_name])
            #print(str(unknowns[0]))
        except Exception as e:
            print("Unknown: " + str(e))

    def do_license(self, arg):
        """."""
        license_name = self.__read_license()
        try:
            expression = self.flame.expression_license(license_name, validations=None, update_dual=False)
            res, err = OutputFormatterFactory.formatter("text").format_expression(expression, self.verbose)
            print(str(res))
            
        except Exception as e:
            print(str(e))

    def do_simplify(self, arg):
        """."""
        license_name = self.__read_license()
        try:
            expression = self.flame.expression_license(license_name, validations=None, update_dual=False)
            simplified = self.flame.simplify([expression['identified_license']])
            res, err = OutputFormatterFactory.formatter("text").format_licenses([str(simplified)], self.verbose)
            print(str(res))
            
        except Exception as e:
            print(str(e))

    def do_verbose(self, arg):
        """Make the interaction more verbose."""
        self.verbose_mode = True
        prompt = '>>> '
        
    def do_silent(self, arg):
        """Make the interaction less verbose (default)."""
        self.verbose_mode = False
        self.prompt = ''

    def __output_result(self, result):
        if self.verbose_mode:
            if not self.formatter:
                self.formatter = OutputFormatterFactory.formatter("text")
            out, err = self.formatter.format_license(result)
            if err:
                print("error" + err, file=sys.stderr)
            print(out)
        else:
            print(str(result['normalized']))


if __name__ == '__main__':
    FlameShell().cmdloop()
