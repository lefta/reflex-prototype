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

from arpeggio import ParserPython
from typing import List, Optional, Tuple

class Failure(Exception):
  def __init__(self, severity: int, pos: int, msg: str, file: Optional[str]) -> None:
    self.severity: int = severity
    self.pos: int = pos
    self.msg: str = msg
    self.file: Optional[str] = file
    self.linecol: Optional[Tuple[int, int]] = None

  def __str__(self) -> str:
    assert self.linecol is not None and self.file is not None
    return self.file + ':' + str(self.linecol[0]) + ':' + str(self.linecol[1]) + ': ' + self.msg

class ParseError(Exception):
  class Severity:
    Warning = 1
    Error = 2
    Fatal = 3

  def __init__(self, failures: List[Failure], parser: Optional[ParserPython] =None) -> None:
    self.failures: List[Failure] = failures
    self.max_level: int = -1
    self.errors: int = 0
    self.warnings: int = 0
    if parser is not None:
      for f in failures:
        if f.severity > self.max_level: self.max_level = f.severity
        if f.severity is ParseError.Severity.Warning: self.warnings += 1
        else: self.errors += 1
        f.linecol = parser.pos_to_linecol(f.pos)

  @property
    if self.warnings is 0: return 'build finished with %d errors' % self.errors
    elif self.errors is 0: return 'build finished with %d warnings' % self.warnings
    else: return 'build finished with %d errors and %d warnings' % (self.errors, self.warnings)
  def summary(self) -> str:

  def __str__(self) -> str:
    res: List[str] = []
    for f in self.failures:
      res.append(str(f))
    return '\n'.join(res) + '\n'
