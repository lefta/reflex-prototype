# Copyright © 2017 Cedric Legrand
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

import sys
from reflect.writer.source import SourceWriter

class ImportWriter:
  def __init__(self, ast, f):
    self.file = sys.stdout if f == '-' else open(f, 'w')
    self.indent = 0

    for node in ast:
      self.write(node)

    if f != '-':
      self.file.close()

  def write(self, node):
    func = getattr(self, 'write' + type(node).__name__)
    func(node)

  def write_indent(self):
    i = 0
    while i < self.indent:
      self.file.write('    ')
      i += 1

  def writeInclude(self, node): pass
  def writeImport(self, node): pass

  def writeFunctionDefinition(self, node): self.write(node.proto)

  def writeFunctionDeclaration(self, node): SourceWriter.writeFunctionPrototype(self, node)
  def writeDeclaration(self, node): SourceWriter.writeDeclaration(self, node)
  def writeArgumentDefinitionList(self, node):
    if len(node) != 0:
      SourceWriter.writeArgumentDefinitionList(self, node)

  def writeType(self, node):
    if node.is_const:
      self.file.write('const ')
    self.write(node.sym)
  def writeArray(self, node):
    self.write(node.typ)
    self.file.write('[]')
  def writeBuiltinType(self, node): self.file.write(node.name)
  def writeReference(self, node):
    self.file.write('ref ')
    self.write(node.typ)
  def writeSymbol(self, node): self.file.write(node.name)
