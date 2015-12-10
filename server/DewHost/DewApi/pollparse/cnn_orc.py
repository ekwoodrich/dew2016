import os
from arpeggio import *
from arpeggio import RegExMatch as _

def Number():	return _'\d'_
def String(): return _'"', None, '"'_

def Month(): return ['Jan', 'Feb']

def Percentage(): return Number, "%"
def Asterisk(): return '*'
def Missing(): return '---'

def Parenthetical(): return '(', None ,')'
def QuestionNumber(): return Number, '.'
def QuestionString(): return OneOrMore([Parenthetical, String])

def Question(): return Optional(QuestionNumber), QuestionString
