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
        elements = line.split()
        for i in range(len(elements)):
            if elements[i] == "WITH":
                elements[i] = ' ( "WITH" | "with" )'
            elif elements[i] == "OR":
                elements[i] = ' ( "OR" | "or" )'
            elif elements[i] == "AND":
                elements[i] = ' ( "AND" | "and" )'
            else:
                # this is license id
                elements[i] = '"{}"i'.format(elements[i])
        if len(elements) > 1:
            elements.insert(0, "(")
            elements.append(")")
        line = ' '.join(elements)

        ITEMS[line] = 1

grammar += "license_item: {0}".format('|'.join(ITEMS.keys()))

print(grammar)
