parser grammar WappaParser;

options {
    tokenVocab = WappaLexer;
}

start: (functionDeclaration)*;

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

functionDeclaration:
    FUN typeOrVoid IDENTIFIER ('(' parameterList? ')')? block;

parameterList:
    IDENTIFIER ':' typeOrVoid (',' IDENTIFIER ':' typeOrVoid)*;

block: '{' statement* '}';

functionCall:
    IDENTIFIER '(' expressionList? ')'
    | 'self' '(' expressionList? ')'
    | 'super' '(' expressionList? ')';

statement: expression ';';

expression:
    primary
    | expression bop = '.' (
        IDENTIFIER
        | functionCall
        | 'self'
        // | NEW nonWildcardTypeArguments? innerCreator
        | 'super' superSuffix
        // | explicitGenericInvocation
    )
    | expression '[' expression ']'
    | functionCall
    | 'new' typeName arguments
    | '(' typeName ')' expression
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
    | 'self'
    | 'super'
    | literal
    | 'let'? IDENTIFIER;

superSuffix: arguments | '.' IDENTIFIER arguments?;

arguments: '(' expressionList? ')';

typeOrVoid: (typeName | 'void');

typeName: IDENTIFIER;