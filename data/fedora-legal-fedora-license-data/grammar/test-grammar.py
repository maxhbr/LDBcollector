#!/usr/bin/python3
import argparse
import os.path
import sys
from lark import Lark
#from lark.exceptions import LarkError

parser = argparse.ArgumentParser(description='Test grammar file')
parser.add_argument('--file', help='read the grammar from this file (default full-grammar.lark)')
opts = parser.parse_args()

if opts.file:
    filename = opts.file
else:
    filename = "full-grammar.lark"

if not os.path.exists(filename):
    print("The file {0} does not exists.".format(filename))
    sys.exit(128)

with open(filename) as f:
    grammar = f.read()

lark_parser = Lark(grammar)  # Scannerless Earley is the default

# Example how to parse
#try:
#    lark_parser.parse(text)
#    # text is OK
#except LarkError as e:
#    # an issue in text
#    print(e)
#    if opts.verbose > 0:
#        print("Not a valid license string")
#    sys.exit(1)
