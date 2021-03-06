# Copyright © 2017-2019 Cedric Legrand
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

import logging
from typing import Callable, cast, List, Sequence, Union
from ehlit.parser.c_header import CDefine, CMacroFunction, CAnyType
from ehlit.parser.ast import (
    Alias, AnonymousArray, Array, ArrayAccess, Assignment, AST, BoolValue, Cast, Char,
    ClassMethod, ClassProperty, CompoundIdentifier, Condition, ControlStructure, DecimalNumber,
    Declaration, Dtor, EhClass, EhEnum, EhUnion, EnumField, Expression, ForDoLoop, FunctionCall,
    Function, FunctionType, HeapAlloc, HeapDealloc, Identifier, Include, Import, InitializationList,
    Namespace, Node, NullValue, Number, Operator, PrefixOperatorValue, ReferenceToType,
    ReferenceToValue, Return, Sizeof, Statement, String, Struct, SuffixOperatorValue, SwitchCase,
    SwitchCaseBody, SwitchCaseTest, Symbol, TemplatedIdentifier, VariableAssignment,
    VariableDeclaration
)

IndentedFnType = Callable[['DumpWriter', Union[Node, str]], None]


def indent(fn: IndentedFnType) -> Callable[..., None]:
    def fn_wrapper(cls: 'DumpWriter', node: Union[Node, str], is_next: bool = True) -> None:
        cls.increment_prefix(is_next)
        fn(cls, node)
        cls.decrement_prefix()
    return fn_wrapper


class DumpWriter:
    def __init__(self, ast: AST) -> None:
        self.prefix: str = ''
        logging.debug('')
        logging.debug('--- AST ---')
        i: int = 0
        count: int = len(ast)
        self.prev_have_next: bool = count > 1
        self.upd_prefix: bool = False
        while i < count:
            self.print_node(ast[i], i < count - 1)
            i += 1

    def dump(self, string: str) -> None:
        logging.debug('%s%s', self.prefix, string)

    def decrement_prefix(self) -> None:
        self.prefix = self.prefix[:-3]
        self.upd_prefix = False

    def increment_prefix(self, is_next: bool) -> None:
        if self.upd_prefix:
            self.prefix = self.prefix[:-3]
            if self.prev_have_next:
                self.prefix += '\u2502  '
            else:
                self.prefix += '   '
            self.upd_prefix = False

        self.prev_have_next = is_next
        if is_next:
            self.prefix += '\u251c' + '\u2500 '
        else:
            self.prefix += '\u2514' + '\u2500 '
        self.upd_prefix = True

    def print_node(self, node: Node, is_next: bool = True) -> None:
        func = getattr(self, 'dump' + type(node).__name__)
        func(node, is_next)

    def print_node_list(self, string: str, lst: Sequence[Node], is_next: bool = True) -> None:
        self.increment_prefix(is_next)
        self.dump(string)
        i: int = 0
        cnt: int = len(lst)
        while i < cnt:
            self.print_node(lst[i], i < cnt - 1)
            i += 1
        self.decrement_prefix()

    @indent
    def print_str(self, s: Union[Node, str]) -> None:
        s = cast(str, s)
        self.dump(s)

    @indent
    def dumpInclude(self, inc: Union[Node, str]) -> None:
        inc = cast(Include, inc)
        self.dump('Include')
        self.print_str('Path: {}'.format(inc.lib))
        self.print_node_list('Symbols found', inc.syms, False)

    @indent
    def dumpImport(self, node: Union[Node, str]) -> None:
        node = cast(Import, node)
        self.dump('Import')
        self.print_str('Path: {}'.format(node.lib))
        self.print_node_list('Symbols found', node.syms, False)

    def dump_declaration(self, decl: Union[Node, str], is_next: bool = True) -> None:
        decl = cast(Declaration, decl)
        self.print_node(decl.typ_src, decl.sym is not None or is_next)
        if decl.sym is not None:
            self.print_node(decl.sym, is_next)

    def dump_variable_declaration(self, cls_name: str, decl: VariableDeclaration) -> None:
        self.dump(cls_name)
        if decl.private:
            self.print_str('Modifiers: private')
        if decl.static:
            self.print_str('Modifiers: static')
        if decl.assign is not None:
            self.dump_declaration(decl)
            self.print_node(decl.assign, False)
        else:
            self.dump_declaration(decl, False)

    @indent
    def dumpVariableDeclaration(self, decl: Union[Node, str]) -> None:
        decl = cast(VariableDeclaration, decl)
        self.dump_variable_declaration('VariableDeclaration', decl)

    def dump_function(self, cls_name: str, fun: Function) -> None:
        self.dump(cls_name)
        if fun.body_str is None:
            self.print_str('Declaration')
        if fun.sym is not None:
            self.print_node(fun.sym)
        self.dump_qualifiers(fun)
        self.print_node(fun.typ, fun.body_str is not None)
        if fun.body_str is not None:
            self.print_node_list('Body', fun.body, False)

    @indent
    def dumpFunction(self, fun: Union[Node, str]) -> None:
        fun = cast(Function, fun)
        self.dump_function('Function', fun)

    @indent
    def dumpStatement(self, stmt: Union[Node, str]) -> None:
        stmt = cast(Statement, stmt)
        self.dump('Statement')
        self.print_node(stmt.expr, False)

    def dumpExpression(self, expr: Union[Node, str], is_next: bool) -> None:
        expr = cast(Expression, expr)
        self.print_node_list('Expression', expr.contents, is_next)

    def dumpInitializationList(self, node: Union[Node, str], is_next: bool) -> None:
        node = cast(InitializationList, node)
        self.print_node_list('InitializerList', node.contents, is_next)

    @indent
    def dumpCast(self, node: Union[Node, str]) -> None:
        node = cast(Cast, node)
        self.dump('Cast')
        self.print_node(node.types[0])
        self.print_node(node.arg, False)

    @indent
    def dumpFunctionCall(self, call: Union[Node, str]) -> None:
        call = cast(FunctionCall, call)
        self.dump('FunctionCall')
        self.print_node(call.sym)
        if call.cast:
            self.increment_prefix(True)
            self.dump('Automatic cast')
            self.print_node(call.cast, False)
            self.decrement_prefix()
        self.print_node_list('Arguments', call.args, False)

    @indent
    def dumpArrayAccess(self, arr: Union[Node, str]) -> None:
        arr = cast(ArrayAccess, arr)
        self.dump('ArrayAccess')
        self.print_node(arr.idx)
        self.print_node(arr.child, False)

    @indent
    def dumpVariableAssignment(self, assign: Union[Node, str]) -> None:
        assign = cast(VariableAssignment, assign)
        self.dump('VariableAssignment')
        self.print_node(assign.var)
        self.print_node(assign.assign, False)

    @indent
    def dumpAssignment(self, assign: Union[Node, str]) -> None:
        assign = cast(Assignment, assign)
        self.dump('Assignment')
        if assign.operator is not None:
            self.print_node(assign.operator)
        self.print_node(assign.expr, False)

    @indent
    def dumpControlStructure(self, struct: Union[Node, str]) -> None:
        struct = cast(ControlStructure, struct)
        self.dump('ControlStructure: ' + struct.name)
        if struct.cond is not None:
            self.print_node(struct.cond)
        self.print_node_list("ControlStructureBody", struct.body, False)

    def dumpDoWhileLoop(self, node: Union[Node, str], is_next: bool) -> None:
        self.dumpControlStructure(node, is_next)

    @indent
    def dumpForDoLoop(self, node: Union[Node, str]) -> None:
        node = cast(ForDoLoop, node)
        self.dump('ControlStructure: ' + node.name)
        self.print_node(node.cond)
        self.print_node_list("Initializers", node.initializers)
        self.print_node_list("Actions", node.actions)
        self.print_node_list("ControlStructureBody", node.body, False)

    def dumpCondition(self, cond: Union[Node, str], is_next: bool) -> None:
        cond = cast(Condition, cond)
        self.print_node_list("ConditionBranches", cond.branches, is_next)

    @indent
    def dumpSwitchCase(self, node: Union[Node, str]) -> None:
        node = cast(SwitchCase, node)
        self.dump('Case')
        self.print_node_list('Tests', node.cases)
        self.print_node(node.body, False)

    def dumpSwitchCaseTest(self, node: Union[Node, str], is_next: bool) -> None:
        node = cast(SwitchCaseTest, node)
        if node.test is not None:
            self.print_node(node.test, is_next)
        else:
            self.print_str('default', is_next)

    def dumpSwitchCaseBody(self, node: Union[Node, str], _: bool) -> None:
        node = cast(SwitchCaseBody, node)
        self.print_str('Falls through: ' + ('yes' if node.fallthrough else 'no'))
        self.print_node_list('Body', node.body, False)

    @indent
    def dumpReturn(self, ret: Union[Node, str]) -> None:
        ret = cast(Return, ret)
        self.dump('Return')
        if ret.expr is not None:
            self.print_node(ret.expr, False)

    def dump_qualifiers(self, node: Union[Symbol, Function]) -> None:
        qualifiers: List[str] = []
        if node.qualifiers.is_const:
            qualifiers.append('const')
        if node.qualifiers.is_volatile:
            qualifiers.append('volatile')
        if node.qualifiers.is_restricted:
            qualifiers.append('restrict')
        if node.qualifiers.is_inline:
            qualifiers.append('inline')
        if node.qualifiers.is_private:
            qualifiers.append('private')
        if len(qualifiers) != 0:
            self.print_str('Modifiers: {}'.format(', '.join(qualifiers)))

    @indent
    def dumpReferenceToType(self, ref: Union[Node, str]) -> None:
        ref = cast(ReferenceToType, ref)
        self.dump('Reference')
        self.dump_qualifiers(ref)
        self.print_node(ref.child, False)

    @indent
    def dumpReferenceToValue(self, ref: Union[Node, str]) -> None:
        ref = cast(ReferenceToValue, ref)
        self.dump('Reference')
        self.print_node(ref.child, False)

    @indent
    def dumpOperator(self, op: Union[Node, str]) -> None:
        op = cast(Operator, op)
        self.dump('Operator: ' + op.op)

    @indent
    def dumpArray(self, arr: Union[Node, str]) -> None:
        arr = cast(Array, arr)
        self.dump('Array')
        if arr.length is not None:
            self.print_str('Sub-type:')
            self.increment_prefix(True)
        self.print_node(arr.child, False)
        if arr.length is not None:
            self.decrement_prefix()
            self.print_str('Length:', False)
            self.increment_prefix(False)
            self.print_node(arr.length, False)
            self.decrement_prefix()

    @indent
    def dumpFunctionType(self, node: Union[Node, str]) -> None:
        node = cast(FunctionType, node)
        self.dump('FunctionType')
        self.print_node(node.ret, len(node.args) != 0 or node.is_variadic)
        if len(node.args) != 0:
            self.print_node_list('Arguments:', node.args, node.is_variadic)
        if node.is_variadic:
            if node.variadic_type is None:
                self.print_str('Variadic (C)', False)
            else:
                self.print_str('Variadic:', False)
                self.increment_prefix(False)
                self.print_node(node.variadic_type, False)
                self.decrement_prefix()

    def dumpCompoundIdentifier(self, node: Union[Node, str], is_next: bool) -> None:
        node = cast(CompoundIdentifier, node)
        self.increment_prefix(is_next)
        self.dump('CompoundIdentifier')
        self.dump_qualifiers(node)
        i = 0
        while i < len(node.elems):
            self.print_node(node.elems[i], i < len(node.elems) - 1)
            i += 1
        self.decrement_prefix()

    @indent
    def dumpIdentifier(self, node: Union[Node, str]) -> None:
        node = cast(Identifier, node)
        self.dump('Identifier: ' + node.name)

    @indent
    def dumpTemplatedIdentifier(self, node: Union[Node, str]) -> None:
        node = cast(TemplatedIdentifier, node)
        self.dump('TemplatedIdentifier: ' + node.name)
        self.print_node_list('Types', node.types, False)

    @indent
    def dumpHeapAlloc(self, node: Union[Node, str]) -> None:
        node = cast(HeapAlloc, node)
        self.dump('HeapAlloc')
        self.print_node(node.sym)
        self.print_node_list('Arguments', node.args, False)

    @indent
    def dumpHeapDealloc(self, node: Union[Node, str]) -> None:
        node = cast(HeapDealloc, node)
        self.dump('HeapDealloc')
        self.print_node(node.sym)

    @indent
    def dumpNumber(self, num: Union[Node, str]) -> None:
        num = cast(Number, num)
        self.dump('Number: ' + num.num)

    @indent
    def dumpDecimalNumber(self, node: Union[Node, str]) -> None:
        node = cast(DecimalNumber, node)
        self.dump('DecimalNumber: ' + node.num)

    @indent
    def dumpChar(self, char: Union[Node, str]) -> None:
        char = cast(Char, char)
        self.dump('Character: ' + char.char)

    @indent
    def dumpString(self, string: Union[Node, str]) -> None:
        string = cast(String, string)
        self.dump('String: ' + string.string)

    @indent
    def dumpNullValue(self, stmt: Union[Node, str]) -> None:
        stmt = cast(NullValue, stmt)
        self.dump('NullValue')

    @indent
    def dumpBoolValue(self, node: Union[Node, str]) -> None:
        node = cast(BoolValue, node)
        self.dump('BoolValue: ' + 'true' if node.val is True else 'false')

    @indent
    def dumpPrefixOperatorValue(self, val: Union[Node, str]) -> None:
        val = cast(PrefixOperatorValue, val)
        self.dump('PrefixOperatorValue')
        self.print_str('Operator: %s' % val.op)
        self.print_node(val.val, False)

    @indent
    def dumpSuffixOperatorValue(self, val: Union[Node, str]) -> None:
        val = cast(SuffixOperatorValue, val)
        self.dump('SuffixOperatorValue')
        self.print_str('Operator: %s' % val.op)
        self.print_node(val.val, False)

    @indent
    def dumpAnonymousArray(self, node: Union[Node, str]) -> None:
        node = cast(AnonymousArray, node)
        self.dump('AnonymousArray')
        self.print_node_list('Contents:', node.contents, False)

    @indent
    def dumpSizeof(self, node: Union[Node, str]) -> None:
        node = cast(Sizeof, node)
        self.dump('Sizeof')
        self.print_node(node.sz_typ, False)

    @indent
    def dumpAlias(self, node: Union[Node, str]) -> None:
        node = cast(Alias, node)
        self.dump('Alias')
        self.print_str('From:')
        self.increment_prefix(True)
        self.print_node(node.src_sym, False)
        self.decrement_prefix()
        self.print_str('To:', False)
        self.increment_prefix(False)
        self.print_node(node.dst, False)
        self.decrement_prefix()

    @indent
    def dumpStruct(self, node: Union[Node, str]) -> None:
        node = cast(Struct, node)
        self.dump('Struct')
        self.print_node(node.sym)
        if node.fields is None:
            self.print_str('Forward declaration', False)
        else:
            self.print_node_list('Fields', node.fields, False)

    @indent
    def dumpEhUnion(self, node: Union[Node, str]) -> None:
        node = cast(EhUnion, node)
        self.dump('Union')
        self.print_node(node.sym)
        if node.fields is None:
            self.print_str('Forward declaration', False)
        else:
            self.print_node_list('Fields', node.fields, False)

    @indent
    def dumpClassMethod(self, node: Union[Node, str]) -> None:
        node = cast(ClassMethod, node)
        self.dump_function('ClassMethod', node)

    @indent
    def dumpCtor(self, node: Union[Node, str]) -> None:
        node = cast(ClassMethod, node)
        self.dump('Constructor')
        self.dump_qualifiers(node)
        assert isinstance(node.typ, FunctionType)
        if len(node.typ.args) != 0:
            self.print_node_list('Arguments:', node.typ.args)
        if node.typ.is_variadic:
            self.print_str('Variadic:')
            self.increment_prefix(False)
            assert node.typ.variadic_type is not None
            self.print_node(node.typ.variadic_type, False)
            self.decrement_prefix()
        self.print_node_list('Body', node.body, False)

    @indent
    def dumpDtor(self, node: Union[Node, str]) -> None:
        node = cast(Dtor, node)
        self.dump('Destructor')
        self.dump_qualifiers(node)
        self.print_node_list('Body', node.body, False)

    @indent
    def dumpClassProperty(self, node: Union[Node, str]) -> None:
        node = cast(ClassProperty, node)
        self.dump_variable_declaration('ClassProperty', node)

    @indent
    def dumpEhClass(self, node: Union[Node, str]) -> None:
        node = cast(EhClass, node)
        self.dump('Class')
        self.print_node(node.sym)
        if node.contents is None:
            self.print_str('Forward declaration', False)
        else:
            self.print_node_list('Properties', node.properties)
            self.print_node_list('Methods', node.methods, len(node.ctors) != 0)
            for ctor in node.ctors:
                self.print_node(ctor, ctor != node.ctors[-1] or node.dtor is not None)
            if node.dtor is not None:
                self.print_node(node.dtor, False)

    @indent
    def dumpEhEnum(self, node: Union[Node, str]) -> None:
        node = cast(EhEnum, node)
        self.dump('Enum')
        self.print_node(node.sym)
        if node.fields is None:
            self.print_str('Forward declaration', False)
        else:
            self.print_node_list('Fields', node.fields, False)

    @indent
    def dumpEnumField(self, node: Union[Node, str]) -> None:
        node = cast(EnumField, node)
        self.dump(node.name)

    @indent
    def dumpNamespace(self, node: Union[Node, str]) -> None:
        node = cast(Namespace, node)
        self.dump('Namespace')
        self.print_node(node.sym)
        self.print_node_list('Contents', node.contents, False)

    @indent
    def dumpCDefine(self, node: Union[Node, str]) -> None:
        node = cast(CDefine, node)
        self.dump('C define')
        if node.sym is not None:
            self.print_node(node.sym, False)

    @indent
    def dumpCMacroFunction(self, node: Union[Node, str]) -> None:
        node = cast(CMacroFunction, node)
        self.dump('C function macro')
        if node.sym is not None:
            self.print_node(node.sym)
        assert isinstance(node.typ, FunctionType)
        self.print_str('Arg count: {}'.format(len(node.typ.args)), False)

    @indent
    def dumpCAnyType(self, node: Union[Node, str]) -> None:
        node = cast(CAnyType, node)
        self.dump('No type')
