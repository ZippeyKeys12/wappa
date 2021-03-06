lexer grammar WappaLexer;

//
// Keywords
//

ABSTRACT: 'abstract';
ALIGNOF:  'alignof';
AS:       'as';
// ASSERT:       'assert';
BOOLEAN: 'boolean';
// BREAK:        'break';
BY: 'by';
// CASE:         'case';
// CATCH:        'catch';
CLASS: 'class';
CONST: 'const';
COPY:  'copy';
// CONTINUE:     'continue';
// DEFAULT:      'default';
DO:      'do';
ELSE:    'else';
ELSIF:   'elsif';
END:     'end';
ENUM:    'enum';
EXTENDS: 'extends';
FINAL:   'final';
FITS:    'fits';
// FINALLY:      'finally';
FOR: 'for';
FUN: 'fun';
IF:  'if';
IS:  'is';
// GOTO:         'goto';
IMPLEMENTS: 'implements';
IMPORT:     'import';
INTERFACE:  'interface';
INTERNAL:   'internal';
LET:        'let';
OBJECT:     'object';
OPEN:       'open';
OVERRIDE:   'override';
PACKAGE:    'package';
PARTIAL:    'partial';
PRIVATE:    'private';
PROTECTED:  'protected';
PROTOTYPE:  'prototype';
// PROTOCOL:  'protocol';
PUBLIC:    'public';
RETURN:    'return';
SELF:      'self';
SINGLETON: 'singleton';
SIZEOF:    'sizeof';
// STATIC:       'static';
SUPER: 'super';
// SWITCH:       'switch';
// SYNCHRONIZED: 'synchronized';
// THROW:        'throw';
// THROWS:       'throws';
TRAIT: 'trait';
// TRANSIENT:    'transient';
// TRY:          'try';
TYPEOF:  'typeof';
UNLESS:  'unless';
UNTIL:   'until';
VAL:     'val';
VAR:     'var';
VIRTUAL: 'virtual';
// VOLATILE:     'volatile';
// WHEN:         'when';
WHERE: 'where';
WHILE: 'while';
// WITH:  'with';
// YIELD: 'yield';

// Directive

// D_ENDIF:   '#endif';
// D_IF:      '#if';
// D_IFDEF:   '#ifdef';
// D_INCLUDE: '#include';

//
// Literals / Identifier
//

DECIMAL_LITERAL: ('0' | [1-9] (Digits? | '_'+ Digits)) [lL]?;
HEX_LITERAL:
    '0' [xX] [0-9a-fA-F] ([0-9a-fA-F_]* [0-9a-fA-F])? [lL]?;
OCT_LITERAL:    '0' '_'* [0-7] ([0-7_]* [0-7])? [lL]?;
BINARY_LITERAL: '0' [bB] [01] ([01_]* [01])? [lL]?;

FLOAT_LITERAL: (Digits '.' Digits? | '.' Digits) ExponentPart? [fFdD]?
    | Digits (ExponentPart [fFdD]? | [fFdD]);

HEX_FLOAT_LITERAL:
    '0' [xX] (HexDigits '.'? | HexDigits? '.' HexDigits) [pP] [+-]? Digits [fFdD]?;

BOOL_LITERAL: 'True' | 'False';

STRING_LITERAL:        '\'' StringInner '\'';
INTERP_STRING_LITERAL: '"' StringInner '"';

NIL: 'Nil';

UNIT: 'Unit';

// UNIT_LITERAL: '()';

IDENTIFIER: Letter LetterOrDigit*;

//
// Separators
//

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
SEMI:   ';';
COMMA:  ',';
DOT:    '.';

//
// Operators
//

DASH_ARROW:     '->';
EQ_ARROW:       '=>';
LPIPE:          '<|';
RPIPE:          '|>';
ASSIGN:         '=';
GT:             '>';
LT:             '<';
LSHIFT:         '<<';
RSHIFT:         '>>';
URSHIFT:        '>>>';
BANG:           '!';
TILDE:          '~';
QUESTION:       '?';
SCOPE:          '::';
COLON:          ':';
GT_COLON:       ':>';
LT_COLON:       '<:';
EQUAL:          '==';
PHYS_EQ:        '===';
APPROX_EQ:      '~=';
LE:             '<=';
GE:             '>=';
NOTEQUAL:       '!=';
PHYS_NEQ:       '!==';
AND:            '&&';
OR:             '||';
INC:            '++';
DEC:            '--';
POW:            '**';
ADD:            '+';
SUB:            '-';
MUL:            '*';
DIV:            '/';
INT_DIV:        '//';
BITAND:         '&';
BITOR:          '|';
CARET:          '^';
REM:            '%';
MOD:            '%%';
ADD_ASSIGN:     '+=';
SUB_ASSIGN:     '-=';
POW_ASSIGN:     '**=';
MUL_ASSIGN:     '*=';
DIV_ASSIGN:     '/=';
INT_DIV_ASSIGN: '//=';
AND_ASSIGN:     '&=';
OR_ASSIGN:      '|=';
XOR_ASSIGN:     '^=';
MOD_ASSIGN:     '%=';
LSHIFT_ASSIGN:  '<<=';
RSHIFT_ASSIGN:  '>>=';
URSHIFT_ASSIGN: '>>>=';

//
// Whitespace and comments
//

WS:      [ \r\n\t\u000C]+ -> skip;
COMMENT: '/*' .*? '*/'    -> skip;
// LINE_COMMENT: '#' ~[\r\n\u2028\u2029]* -> skip;

//
// Fragment rules
//

fragment ExponentPart: [eE] [+-]? Digits;

fragment EscapeSequence:
    '\\' [btnfr"'\\]
    | '\\' ([0-3]? [0-7])? [0-7]
    | '\\' 'u'+ HexDigit HexDigit HexDigit HexDigit;
fragment HexDigits:     HexDigit ((HexDigit | '_')* HexDigit)?;
fragment HexDigit:      [0-9a-fA-F];
fragment Digits:        [0-9] ([0-9_]* [0-9])?;
fragment LetterOrDigit: Letter | [0-9];
fragment Letter:        [a-zA-Z_$];
fragment StringInner:   (~["\\\r\n] | EscapeSequence)*;