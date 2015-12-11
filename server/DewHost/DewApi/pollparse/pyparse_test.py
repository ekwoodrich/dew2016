from pyparsing import *
from pprint import PrettyPrinter
from bs4 import BeautifulSoup

soup = BeautifulSoup(open('cnn_orc.xml', 'r').read(), 'html.parser')
page_test = ''
for page in soup.find_all('page'):
    #print page.text.encode('ascii', 'ignore')
    page_test = page.text.encode('ascii', 'ignore')

# Read the input data
filename = "test.json"
FIN      = open(filename)
TEXT     = FIN.read()


char_string = Word(alphas + ':'   "'" + '?' + '"' + '/' + ' ' + '(' + ')' + ':' + ',' + '-' + '.' )
digits = Word(nums)
percentage = (digits + Suppress('%')) | '---' | '*'
question_num = digits + Suppress('.')

table_item = Group(char_string + Group(OneOrMore(percentage)))

page_num = Suppress("-") + digits + Suppress('-')
pollster = 'CNN/WMUR/UNH Poll'
poll_date_yr = Literal('January') | Literal('February') | Literal('March') | Literal('April') | Literal('May') | Literal('June') | Literal('July') | Literal('August') | Literal('September') | Literal('October') | Literal('November') | Literal('December')
date_yr_long = Group(poll_date_yr + Suppress(',') + Word(nums))
poll_footer = Group(Each(pollster + page_num + date_yr_long))

months = Literal('Jan') | Literal('Feb') | Literal('Mar') | Literal('Apr') | Literal('May') | Literal('June') | Literal('July') | Literal('Aug') | Literal('Sept') | Literal('Oct') | Literal('Nov') | Literal('Dec')
table_row = Group(OneOrMore(percentage))

date_yr = Group(months + digits)
digits = Word(nums)
string = Word(alphas + nums +  ':'   "'" + '?' + '"' + '/' + ' ' + '(' + ')' + ':' + ',' + '-' + '.')
quote = Group(QuotedString('"', multiline=True)) | Group(QuotedString('(', endQuoteChar=')', multiline=True))  |  Group(QuotedString('W', endQuoteChar='?', multiline=True)) 
#print page_test
table_header = Group(Group(OneOrMore(months)) + Group(OneOrMore(digits)))
table = Group(table_header + Group(OneOrMore(table_item)))
quote_block = Group(OneOrMore(quote))


num_quote_block = Group(page_num + OneOrMore(quote))
question_block_num = question_num.setResultsName('question_num')
question_block_table = table.setResultsName('question_table')
question_block_quote = quote_block.setResultsName('question_quote')

question_block = Group(question_block_num + question_block_quote + question_block_table)
block  = question_block | table | quote_block  | quote | question_num | poll_footer | percentage | string

group = OneOrMore(block)
# Parse the results
result = group.parseString( TEXT )
#print page_test.encode('ascii', 'ignore')
for item in result:
    print item
    if 'question_num' in item:
        print item.keys()
    

page_num = Suppress("-") + digits + Suppress('-')
string = Word(alphas + nums + ':'   "'" + '?' + '"' + '/' + ' ' + '(' + ')' + ':' + ',' + '-' + '.')
poll_screen = Group('(' + string  + ':)' )
poll_table_choice = Literal('FAVORABLE') | Literal('NEITHER FAV. OR UNFAV. - VOLUNTEERED') | Literal('UNFAVORABLE') | Literal('DK / NEVER HEAR')
poll_table_choice = poll_table_choice | Literal('DEFINITELY DECIDED WHO WILL VOTE FOR') | Literal('LEANING TOWARD SOMEONE') | Literal('STILL TRYING TO DECIDE')
poll_table_choice = poll_table_choice | Literal('FOREIGN POLICY/NATIONAL SECURITY') | Literal('JOBS/ECONOMY') | Literal('IMMIGRATION') | Literal('BUDGET/NATIONAL DEBT') 
poll_table_choice = poll_table_choice | Literal('HEALTH CARE') | Literal('SOCIAL ISSUES') | Literal('TAXES') | Literal('EDUCATION') | Literal('OTHER / DK')





 

percentage = digits + Suppress('%')

table_header = Group(OneOrMore(poll_table_choice))
string_list = Group(OneOrMore(string))

quote = Group(QuotedString('"', multiline=True)) | Group(QuotedString('(', endQuoteChar=')', multiline=True))
poll_question = Group(OneOrMore(quote))

table_column = Group(date_yr + Group(OneOrMore(percentage)))
table = Group(OneOrMore(table_column))
table_full = Group(poll_question + table_header + table)

page = Group(OneOrMore(table_full) + poll_footer)
blocks   =  percentage | page | table_full  | table_header |  poll_footer | table  | date_yr   | Group(digits + '%')  |  string | Group(digits) | '\r\n' 
group  = OneOrMore(blocks)

    

