parser grammar Wappa;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: classDeclaration*;

///////////
// Class //
///////////

classDeclaration:
    classModifiers 'class' IDENTIFIER classParentDeclaration? classInterfaceDeclaration? classBlock;

classModifiers:
    visibilityModifier? inheritanceModifier? scopeModifier?;

classParentDeclaration:
    'extends' (IDENTIFIER | innerConstructorCall);

classInterfaceDeclaration: 'implements' interfaceSpecifierList;

interfaceSpecifierList:
    interfaceSpecifier (',' interfaceSpecifier)*;

interfaceSpecifier: IDENTIFIER (BY IDENTIFIER)?;

innerConstructorCallList:
    innerConstructorCall (',' innerConstructorCall)*;

innerConstructorCall: functionCall;

// constructorDeclaration:
//     visibilityModifier? IDENTIFIER;

// constructorParameter:
//     staticTypedVar? variableDeclaratorId ':' typeName (
//         '=' variableInitializer
//     )?;

classBlock: '{' memberDeclaration* '}' | ';';

memberDeclaration: fieldDeclaration | functionDeclaration;

fieldDeclaration:
    visibilityModifier? staticTypedVar variableDeclaratorId (
        (':' typeName) ('=' ( literal | innerConstructorCall))?
        | (':' typeName)? ('=' ( literal | innerConstructorCall))
    ) ('{' (IDENTIFIER block)+ '}')? ';';

//////////////
// Function //
//////////////

functionModifiers:
    immutable = 'const'? override = 'override'? visibilityModifier? inheritanceModifier?;

functionDeclaration:
    functionModifiers 'fun' IDENTIFIER ('(' parameterList? ')') (
        '->' typeOrVoid
    )? block;

parameterList:
    IDENTIFIER ':' typeOrVoid (',' IDENTIFIER ':' typeOrVoid)*;

functionCall:
    IDENTIFIER '(' functionArguments? ')'
    | 'self' '(' functionArguments? ')'
    | 'super' '(' functionArguments? ')';

functionArguments: functionArgument (',' functionArgument)*;

functionArgument: (IDENTIFIER ':')? expression;

//////////////
// Variable //
//////////////

variableDeclarations:
    variableDeclaration (',' variableDeclaration)*;

variableDeclaration:
    (
        staticTypedVar variableDeclaratorId (
            ':' typeName
            | '=' variableInitializer
        )
    ) ';';

variableDeclaratorId: IDENTIFIER;

variableInitializer: expression;

////////////////////////////
// Expression / Statement //
////////////////////////////

block: '{' statement* '}';

statement:
    blockLabel = block
    | statementType = 'if' '(' expression ')' block (
        'elsif' '(' expression ')' block
    )* ('else' block)?
    | statementType = 'for' '(' forControl ')' block
    | statementType = 'while' '(' expression ')' block
    | statementType = 'until' '(' expression ')' block
    | statementType = 'do' block doType = 'while' '(' expression ')' ';'
    | statementType = 'do' block doType = 'until' '(' expression ')' ';'
    | statementType = 'return' expression? ';'
    // | classDeclaration
    // | functionDeclaration
    | variableDeclaration
    | ';'
    | expression ';';

forControl:
    variableDeclarations* ';' expression? ';' forUpdate = expressionList?;

expressionList: expression (',' expression)*;

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
    | functionCall
    | classDeclaration
    | typeName arguments
    | expression 'as' typeName
    | expression postfix = ('++' | '--')
    | prefix = ('+' | '-' | '++' | '--') expression
    | prefix = ('~' | '!') expression
    | prefix = ('alignof' | 'sizeof' | 'typeof') expression
    | expression bop = '**' expression
    | expression bop = ( '*' | '/' | '%') expression
    | expression bop = ('+' | '-') expression
    | expression bop = ('<<' | '>>' | '>>>') expression
    | expression top = '<' expression '<' expression
    | expression top = '>' expression '>' expression
    | expression bop = ('<=' | '>=' | '>' | '<' | '<=>') expression
    | expression bop = 'is' typeName
    | expression bop = ('==' | '===' | '!=' | '!==') expression
    | expression bop = '&' expression
    | expression bop = '^' expression
    | expression bop = '|' expression
    | expression bop = '&&' expression
    | expression bop = '||' expression
    | expression top = '?' expression ':' expression
    | expression bop = '|>' expression
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
        | '<<='
        | '>>='
        | '>>>='
        | '%='
    ) expression;

primary:
    '(' expression ')'
    | 'self'
    | 'super'
    | literal
    | IDENTIFIER;

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

staticTypedVar: 'var' | 'val';

typeOrVoid: (typeName | 'void');

typeName: IDENTIFIER typeArguments? typeConstraints?;

typeNameList: typeName (',' typeName)*;

typeArguments: '<' typeNameList '>';

typeConstraints: '[' /* TODO */ ']';

visibilityModifier:
    'private'
    | 'protected'
    | 'internal'
    | 'public';

inheritanceModifier: 'abstract' | 'final' | 'open';

scopeModifier: 'play' | 'ui';

identifierList: IDENTIFIER (',' IDENTIFIER)*;