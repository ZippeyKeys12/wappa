parser grammar WappaParser;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: expression*;

literal:
    integerLiteral
    | floatLiteral
    | STRING_LITERAL
    | BOOL_LITERAL
    | NIL_LITERAL;

integerLiteral:
    DECIMAL_LITERAL
    | HEX_LITERAL
    | OCT_LITERAL
    | BINARY_LITERAL;

floatLiteral: FLOAT_LITERAL | HEX_FLOAT_LITERAL;

expressionList: expression (',' expression)*;

functionCall:
    IDENTIFIER '(' expressionList? ')'
    | SELF '(' expressionList? ')'
    | SUPER '(' expressionList? ')';

expression:
    primary
    | expression bop = '.' (
        IDENTIFIER
        | functionCall
        | SELF
        // | NEW nonWildcardTypeArguments? innerCreator
        | SUPER superSuffix
        // | explicitGenericInvocation
    )
    | expression LBRACK expression RBRACK
    | functionCall
    | NEW IDENTIFIER arguments
    | LPAREN IDENTIFIER RPAREN expression
    | expression postfix = ('++' | '--')
    | prefix = ('+' | '-' | '++' | '--') expression
    | prefix = ('~' | '!') expression
    | expression bop = ('*' | '/' | '%') expression
    | expression bop = ('+' | '-') expression
    | expression ('<' '<' | '>' '>' '>' | '>' '>') expression
    | expression bop = ('<=' | '>=' | '>' | '<') expression
    // | expression bop = INSTANCEOF typeType
    | expression bop = ('==' | '!=') expression
    | expression bop = '&' expression
    | expression bop = '^' expression
    | expression bop = '|' expression
    | expression bop = '&&' expression
    | expression bop = '||' expression
    | expression bop = '?' expression ':' expression
    | <assoc = right> expression bop = (
        '='
        | '+='
        | '-='
        | '**='
        | '*='
        | '/='
        | '&='
        | '|='
        | '^='
        | '>>='
        // | '>>>='
        | '<<='
        | '%='
    ) expression;

primary:
    LPAREN expression RPAREN
    | SELF
    | SUPER
    | literal
    | IDENTIFIER
    | (IDENTIFIER | VOID) '.' CLASS;

createdName: IDENTIFIER ('.' IDENTIFIER)*;

superSuffix: arguments | '.' IDENTIFIER arguments?;

arguments: '(' expressionList? ')';