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
    '{' (variableDeclaration | functionDeclaration)* '}';

functionDeclaration:
    FUN IDENTIFIER ('(' parameterList? ')')? ('->' typeOrVoid)? block;

parameterList:
    IDENTIFIER (':' typeOrVoid)? (
        ',' IDENTIFIER (':' typeOrVoid)?
    )*;

block: '{' (variableDeclaration | statement)* '}';

functionCall:
    IDENTIFIER '(' expressionList? ')'
    | SELF '(' expressionList? ')'
    | SUPER '(' expressionList? ')';

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