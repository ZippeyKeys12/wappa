parser grammar WappaParser;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: (
        // Directives
        // includeDirective
        // | ifDirective
        //
        statement
    )*;

//
// Object
//

objectModifiers: visibilityModifier? modifierModifier?;

objectType: 'object' | 'prototype';

objectDeclaration:
    objectModifiers objectType IDENTIFIER classOrObjectMixinDeclaration? classOrObjectBlock;

//
// Class
//

classModifiers: visibilityModifier? modifierModifier?;

classDeclaration:
    classModifiers 'class' IDENTIFIER constructorDeclaration? classParentDeclaration?
        classInterfaceDeclaration? classOrObjectMixinDeclaration? classOrObjectBlock;

classParentDeclaration: 'extends' innerConstructorCall;

classInterfaceDeclaration: 'implements' interfaceSpecifierList;

classOrObjectMixinDeclaration: 'with' identifierList;

interfaceSpecifierList:
    interfaceSpecifier (',' interfaceSpecifier)*;

interfaceSpecifier: IDENTIFIER (BY IDENTIFIER)?;

innerConstructorCallList:
    innerConstructorCall (',' innerConstructorCall)*;

innerConstructorCall: IDENTIFIER | functionCall;

constructorDeclaration:
    '(' constructorParameter (',' constructorParameter)* ')';

constructorParameter:
    LET? variableDeclaratorId (':' typeName)? (
        '=' variableInitializer
    )?
    | VAR? variableDeclaratorId ':' typeName (
        '=' variableInitializer
    )?;

classOrObjectBlock:
    '{' (fieldDeclaration | functionDeclaration)* '}'
    | ';';

fieldDeclaration:
    (
        LET variableDeclaratorId (':' typeName)?
        | (VAL | VAR) variableDeclaratorId ':' typeName
    ) ('{' (IDENTIFIER block)+ '}')?;

//
// Function
//

functionModifiers: (
        CONST
        | OVERRIDE
        | visibilityModifier
        | modifierModifier
    )+;

functionDeclaration:
    functionModifiers? FUN IDENTIFIER ('(' parameterList? ')')? (
        '->' typeOrVoid
    )? block;

parameterList:
    IDENTIFIER (':' typeOrVoid)? (
        ',' IDENTIFIER (':' typeOrVoid)?
    )*;

functionCall:
    IDENTIFIER '(' functionArguments? ')'
    | SELF '(' functionArguments? ')'
    | SUPER '(' functionArguments? ')';

functionArguments: functionArgument (',' functionArgument)*;

functionArgument: (IDENTIFIER ':')? expression;

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

block:
    '{' (variableDeclaration | functionDeclaration | statement)* '}';

statement:
    blockLabel = block
    | IF '(' expression ')' block (
        ELSIF '(' expression ')' block
    )* (ELSE block)?
    | FOR '(' forControl ')' block
    | WHILE '(' expression ')' block
    | DO block WHILE '(' expression ')' ';'
    | RETURN expression? ';'
    | classDeclaration
    | objectDeclaration
    | functionDeclaration
    | ';'
    | statementExpression = expression (';');

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
    | objectDeclaration
    | classDeclaration
    | NEW typeName arguments
    | COPY IDENTIFIER
    | expression 'as' typeName
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
// Directive
//

// ifDirective:      (D_IF | D_IFDEF) expression ';' .*? D_ENDIF;
// includeDirective: D_INCLUDE STRING_LITERAL;

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

visibilityModifier: PRIVATE | PROTECTED | PUBLIC;

modifierModifier: ABSTRACT | FINAL | OPEN;

identifierList: IDENTIFIER (',' IDENTIFIER)*;