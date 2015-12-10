from pyparsing import *

# Read the input data
filename = "test.json"
FIN      = open(filename)
TEXT     = FIN.read()

# Define a simple grammar for the text, multiply the first col by 2
digits = Word(nums)
months = Group('Jan') | Group('Feb') | Group('Mar') | Group('Apr') | Group('May') | Group('June') | Group('July') | Group('Aug') | Group('Sept') | Group('Oct') | Group('Nov') | Group('Dec')
date_yr = Group(months + digits)
page_num = Group("-" + digits + '-')
string = '"' + Word(alphas) + '"'
poll_screen = Group('(' + alphas  + ':)' )
table_column = Group(date_yr + OneOrMore(Group(digits + '%')))

table_header = ')' + OneOrMore(Group(Word(alphas + nums + ':'   "'" + '?' + '"' + '/' + ' ' + '(' + ')' + ':' + ',' + '-' + '.'))) + '('


table = Group(OneOrMore(table_column))

blocks   = table  | date_yr  |  Group(digits + '%')  | Group(Word(alphas + nums + ':'   "'" + '?' + '"' + '/' + ' ' + '(' + ')' + ':' + ',' + '-' + '.')) | Group(digits) | '\r\n' 
group  = OneOrMore(blocks)

grammar = group
# Parse the results
result = grammar.parseString( TEXT )
# This gives a list of lists
# [['cat', 6], ['dog', 10], ['foo', 14]]

# Open up a new file for the output

# Walk through the results and write to the file
for item in result:
    print item
    

