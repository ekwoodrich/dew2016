import os
from arpeggio import *
from arpeggio import RegExMatch as _

def pollNumber():	return _(r'\d')
def pollString(): return '"', None, '"'

def pollMonth(): return ['Jan', 'Feb']
def pollYear(): return ['Jan', 'Feb']

parsers = ParserPython(pollFile)

current_dir = os.path.dirname(__file__)
testdata = open(os.path.join(currrent_dir, 'db/cnnorc.txt',)).read()

parse_tree = parser.parse(testdata)
print parse_tree