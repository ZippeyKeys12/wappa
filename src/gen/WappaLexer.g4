lexer grammar WappaLexer;

// Keywords
// ABSTRACT:     'abstract';
// ASSERT:       'assert';
BOOLEAN: 'boolean';
// BREAK:        'break';
// CASE:         'case';
// CATCH:        'catch';
CLASS: 'class';
CONST: 'const';
// CONTINUE:     'continue';
// DEFAULT:      'default';
// DO:           'do';
ELSE:  'else';
ELSIF: 'elsif';
// ENUM:         'enum';
// EXTENDS:      'extends';
// FINAL:        'final';
// FINALLY:      'finally';
// FLOAT:        'float';
// FOR:          'for';
FUN: 'fun';
IF:  'if';
// GOTO:         'goto';
// IMPLEMENTS:   'implements';
IMPORT: 'import';
// INSTANCEOF:   'instanceof';
// INTERFACE:    'interface';
LET: 'let';
MY:  'my';
// NATIVE:       'native';
NEW:    'new';
OBJECT: 'object';
// PACKAGE:      'package';
// PRIVATE:      'private';
// PROTECTED:    'protected';
// PUBLIC:       'public';
RETURN: 'return';
SELF:   'self';
// STATIC:       'static';
// STRICTFP:     'strictfp';
SUPER: 'super';
// SWITCH:       'switch';
// SYNCHRONIZED: 'synchronized';
// THIS:         'this';
// THROW:        'throw';
// THROWS:       'throws';
// TRANSIENT:    'transient';
// TRY:          'try';
VAL:  'val';
VAR:  'var';
VOID: 'void';
// VOLATILE:     'volatile';
WHILE: 'while';

// Literals

DECIMAL_LITERAL: ('0' | [1-9] (Digits? | '_'+ Digits)) [lL]?;
HEX_LITERAL:
    '0' [xX] [0-9a-fA-F] ([0-9a-fA-F_]* [0-9a-fA-F])? [lL]?;
OCT_LITERAL:    '0' '_'* [0-7] ([0-7_]* [0-7])? [lL]?;
BINARY_LITERAL: '0' [bB] [01] ([01_]* [01])? [lL]?;

FLOAT_LITERAL: (Digits '.' Digits? | '.' Digits) ExponentPart? [fFdD]?
    | Digits (ExponentPart [fFdD]? | [fFdD]);

HEX_FLOAT_LITERAL:
    '0' [xX] (HexDigits '.'? | HexDigits? '.' HexDigits) [pP] [+-]? Digits [fFdD]?;

BOOL_LITERAL: 'true' | 'false';

STRING_LITERAL: '"' StringInner '"' | '\'' StringInner '\'';

NIL_LITERAL: 'nil';

// Separators

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
SEMI:   ';';
COMMA:  ',';
DOT:    '.';

// Operators

ARROW:         '->';
ASSIGN:        '=';
GT:            '>';
LT:            '<';
BANG:          '!';
TILDE:         '~';
QUESTION:      '?';
SCOPE:         '::';
COLON:         ':';
EQUAL:         '==';
LE:            '<=';
GE:            '>=';
NOTEQUAL:      '!=';
AND:           '&&';
OR:            '||';
INC:           '++';
DEC:           '--';
POW:           '**';
ADD:           '+';
SUB:           '-';
MUL:           '*';
DIV:           '/';
BITAND:        '&';
BITOR:         '|';
CARET:         '^';
MOD:           '%';
ADD_ASSIGN:    '+=';
SUB_ASSIGN:    '-=';
POW_ASSIGN:    '**=';
MUL_ASSIGN:    '*=';
DIV_ASSIGN:    '/=';
AND_ASSIGN:    '&=';
OR_ASSIGN:     '|=';
XOR_ASSIGN:    '^=';
MOD_ASSIGN:    '%=';
LSHIFT_ASSIGN: '<<=';
RSHIFT_ASSIGN: '>>=';
// URSHIFT_ASSIGN: '>>>=';

// Whitespace and comments
WS:           [ \t\r\n\u000C]+          -> skip;
COMMENT:      '/*' .*? '*/'             -> skip;
LINE_COMMENT: '//' ~[\r\n\u2028\u2029]* -> skip;

// Identifiers
IDENTIFIER: Letter LetterOrDigit*;

// Fragment rules
fragment ExponentPart: [eE] [+-]? Digits;

fragment EscapeSequence:
    '\\' [btnfr"'\\]
    | '\\' ([0-3]? [0-7])? [0-7]
    | '\\' 'u'+ HexDigit HexDigit HexDigit HexDigit;
fragment HexDigits:     HexDigit ((HexDigit | '_')* HexDigit)?;
fragment HexDigit:      [0-9a-fA-F];
fragment Digits:        [0-9] ([0-9_]* [0-9])?;
fragment LetterOrDigit: Letter | [0-9];
fragment Letter:
    [a-zA-Z$_]
    | ~[\u0000-\u007F\uD800-\uDBFF]
    | [\uD800-\uDBFF] [\uDC00-\uDFFF];
fragment StringInner: (~["\\\r\n] | EscapeSequence)*;