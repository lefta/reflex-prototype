# Copyright © 2017-2018 Cedric Legrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from arpeggio import ParserPython, visit_parse_tree, NoMatch, StrMatch
from typing import List

from ehlit.parser.grammar import grammar, function_body_grammar, Context
from ehlit.parser.ast_builder import ASTBuilder
from ehlit.parser.error import ParseError, Failure


def handle_parse_error(err, parser):
  exp: List[str] = []
  for r in err.rules:
    if type(r) is StrMatch:
      r = "'%s'" % str(r)
    else:
      r = str(r)
    if r not in exp:
      exp.append(r)
  raise ParseError([Failure(ParseError.Severity.Fatal, err.position,
                            'expected %s' % (' or '.join(exp)), parser.file_name)], parser)


def parse(source):
  parser = ParserPython(grammar, autokwd=True, memoization=True)
  try:
    parsed = parser.parse_file(source)
    ast = visit_parse_tree(parsed, ASTBuilder())
    ast.parser = parser
  except NoMatch as err:
    handle_parse_error(err, parser)
  return ast


def parse_function(source, have_return_value):
  Context.return_value = have_return_value
  parser = ParserPython(function_body_grammar, autokwd=True, memoization=True)
  try:
    parsed = parser.parse(source)
    body = visit_parse_tree(parsed, ASTBuilder())
  except NoMatch as err:
    handle_parse_error(err, parser)
  return body
