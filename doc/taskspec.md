Grader specifier file (task.spec)
=================================

The grader specifier file (usually called *task.spec*) is the file that contains all of the information needed for the generation of the graders (and templates). Not exactly *all* the information, as we will see, but the vast majority.

This file should always be present in a subdirectory of the directory of execution of gradergen (or at the path passed with the flag --taskspec). The name of the specifier is not enforced, but it is suggested to call it task.spec (or at least to give it the .spec extension).

General notions on the syntax
-----------------------------
The specifier follows a strict syntax for describing how the grader should read/write and interact with the user program.

Comments must be full line and are identified by the '#' character. Any line starting with # is ignored by the parser.

The specifier file must contains the following sections:
* variables
* prototypes
* input
* calls
* output  

The order is not enforced, but we suggest to follow the above one, as it is the same in which sections are processed by gradergen.  
Each section should be present exactly once (may be empty) and its start is denoted by `***name_of_the_section***`.
The section ends when the next one starts (or when the file ends).

Summing up, the global structure of *task.spec* should be:
```
# Some comments
# Lines beginning with # and empty lines are ignored.

***variables***
...variables specifications...

***prototypes***
...prototypes specifications...

***input***
# Comments can be anywhere in the files, not only at the beginning!
...input specifications...

***calls***
...calls specifications...

***output***
...output specifications...


```

Now we will describe each section carefully.

Variables
---------
This section contains the declarations of all the variables used in the grader.  
Each line contains the declaration of a single variable.

There are two type of variables: primitive type variables and arrays.
We will describe the two syntaxes separately:

#### Primitive type variables  
A line describing a simple variable has the following structure:
```
type_identifier variable_name
``` 
The possible type's identifiers are listed in the [proper section](#types-identifiers).  
The name of the variable can contain letters, digits and underscores and cannot begin with a digit.  

The line is saying that the variable with name `variable_name` is of the given type.

#### Primitive type variables  
A line describing a simple variable has the following structure:
```
type_identifier array_name[size1][size2]...[sizen]
``` 
Everything about the type identifier and the name is exactly as it is for [primitive type variables](#primitive-type-variables), so we suggest to look there for further details.   
The sizes have to be expressions, for details about expressione see the [appriopriate section](#expressions). The dimension of the array (the number of sizes) is not limited, even if multidimensional array are not supported in every languages.

The line means that the variable with name `array_name` is a multidimensional array with sizes size1, size2, ..., sizen and its primitive type is the given one.

## Prototypes
TODO

## Input
TODO

## Calls
TODO

## Output
TODO

Appendix
--------
### Type's identifiers
The type's identifiers are the following ones:
* `int`: An simple integer (32 bit).
* `longint`: A long integer (64 bit).
* `char`: A single character.
* `real`: A floating point number (usually a double floating point using 64 bit).
* `empty string`: The empty identifier can be used only as the returning value of a function. It means that the function is not returning anything.

### Expressions
An expression is an affine dependence on a variable: `a*variable_name+b` where `a` and `b` have to be numbers. The `variable_name` must refer to a variable with type `int` or `longint`.  
The syntax to use in *task.spec* to define an expression is not strict and any of the following is a valid expression:
```
variable_name
variable_name+10
variable_name-20
5*variable
-7*variable+134
```

### References in various languages
With the word reference we mean a variable that is passed to a function and the function has access to that same variable, not to a copy of it. [Here](https://en.wikipedia.org/wiki/Reference_(computer_science)) you can find a deeper explanation of the concept of reference.

Parameters passed by reference are handled as shown in each language:
* *C++* The function is declared with a parameter passed by reference using the character '&' before the parameter name. In the case of arrays, they are not passed by reference as they are already pointer.
* *C* As references are non existent in pure *C*, references are faked using pointer. So instead of passing the value to the function, a pointer to the value is passed instead. As for *C++*, nothing is done for arrays parameters as they are already passed as pointers.
* *pascal* TODO
