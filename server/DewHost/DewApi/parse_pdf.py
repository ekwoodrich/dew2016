from bs4 import BeautifulSoup
import re

soup = BeautifulSoup(open('db/cnn_orc'), 'lxml')

page = unicode(soup.find_all('page')[1].text)
page = page.replace(u"\u2018", "\'").replace(u"\u2019", "\'").replace(u"\u201c","\"").replace(u"\u201d", "\"")


for number in re.findall(r"(\d)\.+\s*[\",\(]",page):
	print number
for question in re.findall(r"\d\.+\s*[\",\(](.*?)[\?,\.]\"",page):
	print "QUESTION"
	print question.encode('ascii', 'ignore').replace(")", "").replace("\"", "")
#for question in re.findall(r"\"(.*?)[\?,\.]\"",page):
#	print "QUESTION"
#	print question.encode('ascii', 'ignore')



#print page.encode('ascii', 'ignore')
