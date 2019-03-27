parser grammar Wappa;

options {
    tokenVocab = WappaLexer;
}

compilationUnit: classDeclaration*;

///////////
// Class //
///////////

classDeclaration:
    classModifiers 'class' IDENTIFIER constructorDeclaration? classParentDeclaration?
        classInterfaceDeclaration? classBlock;

classModifiers: visibilityModifier? inheritanceModifier?;

classParentDeclaration:
    'extends' (IDENTIFIER | innerConstructorCall);

classInterfaceDeclaration: 'implements' interfaceSpecifierList;

interfaceSpecifierList:
    interfaceSpecifier (',' interfaceSpecifier)*;

interfaceSpecifier: IDENTIFIER (BY IDENTIFIER)?;

innerConstructorCallList:
    innerConstructorCall (',' innerConstructorCall)*;

innerConstructorCall: functionCall;

constructorDeclaration:
    '(' constructorParameter (',' constructorParameter)* ')';

constructorParameter:
    'let'? variableDeclaratorId (':' typeName)? (
        '=' variableInitializer
    )?
    | staticTypedVar? variableDeclaratorId ':' typeName (
        '=' variableInitializer
    )?;

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
    'const'? 'override'? visibilityModifier? inheritanceModifier?;

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
        'let' variableDeclaratorId (':' typeName)? (
            '=' variableInitializer
        )?
        | staticTypedVar variableDeclaratorId (
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
    | 'if' '(' expression ')' block (
        'elsif' '(' expression ')' block
    )* ('else' block)?
    | 'for' '(' forControl ')' block
    | 'while' '(' expression ')' block
    | 'do' block 'while' '(' expression ')' ';'
    | 'return' expression? ';'
    | classDeclaration
    | functionDeclaration
    | variableDeclaration
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
    | expression bop = '**' expression
    | expression bop = ( '*' | '/' | '%') expression
    | expression bop = ('+' | '-') expression
    | expression bop = ('<<' | '>>') expression
    | expression bop = ('<=' | '>=' | '>' | '<') expression
    | expression bop = 'is' typeName
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
        | '<<='
        | '%='
    ) expression;

primary:
    '(' expression ')'
    | 'self'
    | 'super'
    | literal
    | 'let'? IDENTIFIER;

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

typeName: IDENTIFIER;

visibilityModifier:
    'private'
    | 'protected'
    | 'internal'
    | 'public';

inheritanceModifier: 'abstract' | 'final' | 'open';

identifierList: IDENTIFIER (',' IDENTIFIER)*;