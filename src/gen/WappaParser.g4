parser grammar WappaParser;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: (
        classDeclaration
        | objectDeclaration
        | functionDeclaration
    )*;

//
// Class / Object
//

classDeclaration:
    CLASS IDENTIFIER constructorDeclaration? (
        classOrObjectBlock
        | ';'
    );

constructorDeclaration:
    '(' constructorParameter (',' constructorParameter)* ')';

constructorParameter:
    LET? variableDeclaratorId (':' typeName)? (
        '=' variableInitializer
    )?
    | VAR? variableDeclaratorId ':' typeName (
        '=' variableInitializer
    )?;

objectDeclaration: OBJECT IDENTIFIER (classOrObjectBlock | ';');

classOrObjectBlock:
    '{' (fieldDeclaration | functionDeclaration)* '}';

fieldDeclaration:
    (
        LET variableDeclaratorId (':' typeName)?
        | (VAL | VAR) variableDeclaratorId ':' typeName
    ) ('{' (IDENTIFIER block)+ '}')?;

//
// Function
//

functionDeclaration:
    FUN IDENTIFIER ('(' parameterList? ')')? ('->' typeOrVoid)? block;

parameterList:
    IDENTIFIER (':' typeOrVoid)? (
        ',' IDENTIFIER (':' typeOrVoid)?
    )*;

functionCall:
    IDENTIFIER '(' expressionList? ')'
    | SELF '(' expressionList? ')'
    | SUPER '(' expressionList? ')';

//
// Variable
//

variableDeclarations:
    variableDeclaration (',' variableDeclaration)*;

variableDeclaration:
    (
        LET variableDeclaratorId (':' typeName)? (
            '=' variableInitializer
        )?
        | VAR variableDeclaratorId (
            ':' typeName
            | '=' variableInitializer
        )
    ) ';';

variableDeclaratorId: IDENTIFIER;

variableInitializer: expression;

//
// Expression / Statement
//

block: '{' (variableDeclaration | statement)* '}';

statement:
    blockLabel = block
    | IF '(' expression ')' block (
        ELSIF '(' expression ')' block
    )* (ELSE block)?
    | FOR '(' forControl ')' block
    | WHILE '(' expression ')' block
    | DO block WHILE '(' expression ')' ';'
    | RETURN expression? ';'
    | ';'
    | statementExpression = expression ';';

forControl:
    variableDeclarations* ';' expression? ';' forUpdate = expressionList?;

expressionList: expression (',' expression)*;

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
    | expression bop = ('<<' | '>>>' | '>>') expression
    | expression bop = ('<=' | '>=' | '>' | '<') expression
    | expression bop = IS typeName
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
        | '>>>='
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

//
// General
//

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

typeOrVoid: (typeName | VOID);

typeName: IDENTIFIER;