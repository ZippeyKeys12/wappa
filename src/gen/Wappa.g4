parser grammar Wappa;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: translationUnit;

translationUnit: (classDeclaration | functionDeclaration)*;

///////////
// Class //
///////////

classDeclaration:
    classModifiers 'class' IDENTIFIER classParentDeclaration? classInterfaceDeclaration? classBlock;

classModifiers: visibilityModifier? inheritanceModifier?;

classParentDeclaration: ':' typeName;

classInterfaceDeclaration: 'implements' interfaceSpecifierList;

interfaceSpecifierList:
    interfaceSpecifier (',' interfaceSpecifier)*;

interfaceSpecifier: IDENTIFIER (BY functionCall)?;

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

memberDeclaration: fieldDeclaration | methodDeclaration;

fieldDeclaration:
    visibilityModifier? staticTypedVar variableDeclaratorId (
        ':' typeName ('=' ( literal | innerConstructorCall))?
        | '=' ( literal | innerConstructorCall)
    ) ('{' (IDENTIFIER block)+ '}')? ';';

//////////////
// Function //
//////////////

functionModifiers:
    immutable = 'const'? override = 'override'? visibilityModifier? inheritanceModifier?;

functionDeclaration:
    functionModifiers 'fun' IDENTIFIER '(' parameterList? ')' (
        '->' typeOrUnit
    )? (block | '=' expression ';');

methodDeclaration:
    functionModifiers 'fun' IDENTIFIER '(' ref = SELF (
        ',' parameterList
    )? ')' ('->' typeOrUnit)? (block | '=' expression ';');

parameterList:
    IDENTIFIER ':' typeExpression (
        ',' IDENTIFIER ':' typeExpression
    )*;

functionCall:
    IDENTIFIER '(' expressionList? functionKwarguments? ')';

functionKwarguments:
    functionKwargument (',' functionKwargument)*;

functionKwargument: IDENTIFIER ':' expression;

//////////////
// Variable //
//////////////

variableDeclarations:
    variableDeclaration (',' variableDeclaration)*;

variableDeclaration:
    staticTypedVar variableDeclaratorId (
        ':' typeName ('=' variableInitializer)?
        | ('=' variableInitializer)
    );

variableDeclaratorId: IDENTIFIER;

variableInitializer: expression;

////////////////////////////
// Expression / Statement //
////////////////////////////

block: '{' statement* '}';

statement:
    blockLabel = block
    | statementType = 'if' ifExpr = expression ifBlock = block (
        'elsif' '(' elsifExpr += expression ')' elsifBlock += block
    )* ('else' elseBlock = block)?
    | statementType = 'for' '(' forControl ')' block
    | statementType = 'while' '(' expression ')' block
    | statementType = 'until' '(' expression ')' block
    | statementType = 'do' block doType = 'while' '(' expression ')' ';'
    | statementType = 'do' block doType = 'until' '(' expression ')' ';'
    | statementType = 'return' expression? ';'
    // | classDeclaration
    // | functionDeclaration
    | variableDeclarations ';'
    | expression ';'
    | ';';

forControl:
    variableDeclarations* ';' expression? ';' forUpdate = expressionList?;

expressionList: expression (',' expression)*;

expression:
    primary
    | expression bop = '.' (
        IDENTIFIER
        | functionCall
        // | 'self'
        // | NEW nonWildcardTypeArguments? innerCreator
        // | 'super' superSuffix
        // | explicitGenericInvocation
    )
    | functionCall
    // | classDeclaration
    // | typeName arguments
    | expression 'as' typeName
    | expression postfix = ('++' | '--')
    | prefix = ('+' | '-' | '++' | '--') expression
    | prefix = ('~' | '!') expression
    | prefix = ('alignof' | 'sizeof' | 'typeof') expression
    | expression bop = '**' expression
    | expression bop = ('*' | '//' | '/' | '%') expression
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
        | '//='
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
    | stringLiteral
    | BOOL_LITERAL
    | NIL_LITERAL;

integerLiteral:
    DECIMAL_LITERAL
    | HEX_LITERAL
    | OCT_LITERAL
    | BINARY_LITERAL;

floatLiteral: FLOAT_LITERAL | HEX_FLOAT_LITERAL;

stringLiteral:  STRING_LITERAL | INTERP_STRING_LITERAL;
staticTypedVar: 'var' | 'val';

typeOrUnit: typeExpression;

typeExpression:
    typeName
    | typeExpression bop = '&' typeExpression
    | typeExpression bop = '|' typeExpression;

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

identifierList: IDENTIFIER (',' IDENTIFIER)*;