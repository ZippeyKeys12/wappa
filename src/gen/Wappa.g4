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

classParentDeclaration: 'extends' typeName;

classInterfaceDeclaration: 'implements' interfaceSpecifierList;

interfaceSpecifierList:
    interfaceSpecifier (',' interfaceSpecifier)*;

interfaceSpecifier: intersectionType (BY functionCall)?;

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
        '=>' returnType
    )? (block | '=' expression ';');

methodDeclaration:
    functionModifiers 'fun' IDENTIFIER '(' 'self' (
        ',' parameterList
    )? ')' ('=>' returnType)? (block | '=' expression ';');

returnType: 'Unit' | trueType;

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
    // | classDeclaration
    // | typeName arguments
    | expression 'as' typeName
    | expression postfix = ('++' | '--')
    | prefix = ('+' | '-' | '++' | '--') expression
    | prefix = ('~' | '!') expression
    | prefix = ('alignof' | 'sizeof' | 'typeof') expression
    | expression bop = '**' expression
    | expression bop = ('*' | '/' | '//' | '%' | '%%') expression
    | expression bop = ('+' | '-') expression
    | expression bop = ('<<' | '>>' | '>>>') expression
    | expression top = '<' expression '<' expression
    | expression top = '>' expression '>' expression
    | expression bop = ('<=' | '>=' | '>' | '<') expression
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

// referenceExpression: (IDENTIFIER | 'self' | 'super') '.' (
//         IDENTIFIER
//         | functionCall
//         | referenceExpression
//     );

referenceExpression: (
        IDENTIFIER
        | 'self'
        | 'super'
        | functionCall
    ) ('.' (IDENTIFIER | functionCall))*;

primary: '(' expression ')' | literal | referenceExpression;

arguments: '(' expressionList? ')';

//
// General
//

literal:
    integerLiteral
    | floatLiteral
    | stringLiteral
    | BOOL_LITERAL
    | 'Nil';

integerLiteral:
    DECIMAL_LITERAL
    | HEX_LITERAL
    | OCT_LITERAL
    | BINARY_LITERAL;

floatLiteral: FLOAT_LITERAL | HEX_FLOAT_LITERAL;

stringLiteral: STRING_LITERAL | INTERP_STRING_LITERAL;

//
// Types
//

trueType: '(' trueType ')' | typeExpression | functionType;

//
// Function Types
//

functionType: functionTypePart ('->' functionTypePart)+;

functionTypePart: typeExpression | innerFunctionType;

innerFunctionType:
    '(' functionTypePart ('->' functionTypePart)+ ')';

//
// Type Expressions
//

typeExpression:
    typeName
    | '(' typeExpression ')'
    | typeExpression bop = '&' typeExpression
    | typeExpression bop = '|' typeExpression;

intersectionType:
    typeName
    | intersectionType '&' intersectionType;

unionType: typeName | unionType '|' unionType;

//
// Type Name
//

typeName: IDENTIFIER typeArguments? typeConstraints?;

trueTypeList: trueType (',' trueType)*;

typeArguments: '<' trueTypeList '>';

typeConstraints: '[' /* TODO */ ']';

//
// Modifiers
//

staticTypedVar: 'var' | 'val';

visibilityModifier:
    'private'
    | 'protected'
    | 'internal'
    | 'public';

inheritanceModifier: 'abstract' | 'final' | 'open';