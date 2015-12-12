from __future__ import unicode_literals

import os
from arpeggio import *
from arpeggio import RegExMatch as _

def number():     return _(r'\d*\.\d*|\d+')
def jsonString():       return _('[^"]*')
def jsonLine():         return [jsonString, number, jsonLine], '"'
def jsonFile():         return OneOrMore(jsonLine), EOF


def main(debug=False):
    # Creating parser from parser model.
    parser = ParserPython(jsonFile, debug=debug)

    # Load test JSON file
    current_dir = os.path.dirname(__file__)
    testdata = open(os.path.join(current_dir, 'test.json')).read().replace('\n', '"')

    # Parse json string
    parse_tree = parser.parse(testdata)

    # parse_tree can now be analysed and transformed to some other form
    # using e.g. visitor support. See http://igordejanovic.net/Arpeggio/semantics/

if __name__ == "__main__":
    main(debug=True)
