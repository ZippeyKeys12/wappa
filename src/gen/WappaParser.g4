parser grammar WappaParser;

options {
    tokenVocab = WappaLexer;
}

start: (
        classDeclaration
        | objectDeclaration
        | functionDeclaration
    )*;

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

classDeclaration: CLASS IDENTIFIER classOrObjectBlock;

objectDeclaration: OBJECT IDENTIFIER classOrObjectBlock;

classOrObjectBlock:
    '{' (fieldDeclaration | functionDeclaration)* '}';

functionDeclaration:
    FUN IDENTIFIER ('(' parameterList? ')')? ('->' typeOrVoid)? block;

parameterList:
    typeOrVoid IDENTIFIER (',' typeOrVoid IDENTIFIER)*;

block: '{' statement* '}';

functionCall:
    IDENTIFIER '(' expressionList? ')'
    | SELF '(' expressionList? ')'
    | SUPER '(' expressionList? ')';

fieldDeclaration:
    variableDeclaratorId ':' typeName ('=' variableInitializer)? ';';

variableDeclaratorId: IDENTIFIER;

variableInitializer: expression;

statement: expression ';';

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
    | expression '[' expression ']'
    | functionCall
    | NEW typeName arguments
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
    | SELF
    | SUPER
    | literal
    | LET? IDENTIFIER;

superSuffix: arguments | '.' IDENTIFIER arguments?;

arguments: '(' expressionList? ')';

typeOrVoid: (typeName | VOID);

typeName: IDENTIFIER;