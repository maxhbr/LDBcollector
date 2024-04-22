#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(description='Create complete LARK grammar.')
parser.add_argument('grammar', help='file with grammar (without licenses)')
parser.add_argument('licenses', help='file with approved licenses')
opts = parser.parse_args()

with open(opts.grammar) as f:
    grammar = f.read()

ITEMS = {}
with open(opts.licenses) as f:
    for line in f:
        if line.isspace():
            continue
        if line.startswith('#'):
            continue
        line = line.strip()
        ITEMS['"{}"i'.format(line)] = 1

grammar += "license_item: {0}".format('|'.join(ITEMS.keys()))

print(grammar)
