
# Grader specifier file (`task.spec`)

The grader specification file (usually called `task.spec`) is the file which contains the information needed to generate graders (and templates). Not exactly *all* of the information, as we will see, but the vast majority.

This file should always be present in a subdirectory of gradergen's working directory (or at the path specified using the flag `--taskspec`). The name of the file is not enforced, but it is suggested to call it `task.spec` (or, at least, to use the `.spec` extension).

## General notions on the syntax

The specification file follows a strict syntax to describe how the grader should read/write and interact with the user program.

Multi-line comments are not supported. Comments are identified by the `#` character. Any line starting with `#` is ignored by the parser.

The specifier file shall contain some of the following sections:

* `variables`
* `prototypes`
* `input`
* `calls`
* `output`  

The order is not enforced, but we suggest to follow the above one, as it is the same in which sections are processed by gradergen.

Each section should be present exactly once (and may be empty) and is denoted by `***name_of_the_section***`.
The section ends when another section starts, or the file ends.

This is a possible `task.spec` file:

```
# Some comments
# Lines beginning with # and empty lines are ignored.

***variables***
int N
char x[N]
char y[N]

int result1
int result2

***prototypes***
doTheThing(int N, char[] x, char[] y, int &result1, int &result2)

***input***
# Comments can be anywhere in the files, not only at the beginning!
N
x[] y[]

***calls***
doTheThing(N, x, y, result1, result2)

***output***
result1 result2
```

Now we will describe each section carefully.

## Variables

This section contains the declarations of all the variables used in the grader. Each line contains the declaration of a single variable.

There are two type of variables: primitive type variables and arrays. We will describe the two syntaxes separately:

#### Primitive type variables  

A line describing a simple variable has the following structure:

```
type_identifier variable_name
``` 

The possible type's identifiers are listed in the [proper section](#types-identifiers). The name of the variable can contain letters (matched by the regex `[a-zA-Z]`), digits and underscores and cannot begin with a digit.

The line states that the variable with name `variable_name` is of the given type.

#### Arrays

A line describing an array has the following structure:

```
type_identifier array_name[size1][size2]...[sizeN]
``` 

Everything about the type identifier and the name is exactly as it is for [primitive type variables](#primitive-type-variables), so we suggest to look there for further details. The sizes have to be expressions, for details about expressione see the [appriopriate section](#expressions). The dimension of the array (the number of sizes) is not limited, even if multidimensional array are not supported in every languages.

The line states that the variable with name `array_name` is a multidimensional array with sizes `size1`, `size2`, ..., `sizen` and its primitive type is the given one.

## Prototypes
In this section you have to declare all the prototypes of the function that will be called by the grader.
Here you have to insert both the functions that should be defined in the contestant source code and both those that are define in the `include_grader` file. For further details about `include_grader` see the [proper section](#the-includegrader-and-includecallable-files).   
This is the only section processed to generate the template.

Each line of this section must contain a prototype for a function. The general syntax of the prototype is:
```
return_type function_name(parameter1, parameter2, ..., parametern)
```
The `return_type` is a type_specifier and obviously is the type of the variable returned by the function.  
After the prototype, on the same line, there might be `{location}` where location can be `grader` or `solution`. If it is `grader` it means that this prototype is defined in `include_grader` and should not be present in the template. The default is `solution`, that means that this function has to be defined in the contestant's code.  

Each parameter must contain the type (arrays are possible), the name (used in the template and in the function declaration in the grader) and whether the parameters should be passed by reference or not. If you want to know more about references see the [section](#references-in-various-languages) focused on them. A parameter should be passed by reference only if the function is expected to modify it.   
The syntax for the parameter definition is the following:
```
type_identifier &parameter_name[][]..[][]
```
The ampersand `&`, if present, means that the parameter should be passed by reference. The sequence of `[]`, if present, means that the parameter is an array and its dimension is the number of pairs of square brackets.

Given all of the informations above you should now understand the meanings of the following correct prototypes:
```
# FindSum returns the sum of a and b
int FindSum(int a, int b)

# This function is defined in the grader and calls N times the function 'int  
# approximate(double)' defined by the contestant. On each call, heights[i] is  
# passed to approximate and the return value is stored in solutions[i].
CallManyTimes(int N, real heights[], int &solutions[]) {grader}

# This function returns the minimum cut relative to the vertexes source and sink in 
# graph passed in the parameters.
longint MinCut(int N, int E, int source, int sink, int from[], int to[], int weight[])
```

## Input
TODO

## Calls
TODO

## Output
TODO

## Appendix

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
5*variable_name
-7*variable_name+134
```

### The `include_grader` and `include_callable` files
These two files contain additional source code to be included in the grader. The reason for their existence is to enrich the capability of the generated graders and make possible to use `gradergen` also for *complex* problems that are not fully expressed by the strict syntax of `task.spec`.  
This files have to be called `include_grader.lang_extension` and `include_callable.lang_extension`, where `lang_extension` is the proper extension of the programming language. If you want `gradergen` to use them they have to be in or in the same directory as `task.spec` or in the directory specified with the flag `--include_dir`.   
If `include_grader` is present for one of the language processed, then it has to be present for all the languages processed. The same applies to `include_callable`.  

The two files obviously have a different content and are processed differently by `gradergen`.
  
*  `include_grader`: This should contain the functions that the grader wants to call but that are not defined in the contestant's source code. These functions should not interact with the variables defined in the grader, but only with those passed by arguments.  
Using `include_grader` is very handy if, for example, the grader wants to call different functions depending on a character in the input. To clarify, a valid `include_grader.cpp` doing what mentioned is:

```C++
void fill_A(int N char X[], int input_values[], int output_values[]) {
	for (int i = 0; i < N; i++) {
		if (X[i] == 'a') output_values[i] = GetAge(input_values[i]);
		else if (X[i] == 'b') output_values[i] = GetBirthday(input_values[i]);
	}
}
```

* `include_callable`: This one contains all the functions that the contestant's program can call. These functions can interact with all the variables defined in the grader. Moreover in this file you can also, accordingly to the language, define new variables. We strongly advise not to do any input or output in this section as IO is handled differently if fast input is enabled or not.   
For example, `include_callable` must be used in problems where the contestant's program can ask questions and the final score depends on the number of questions asked.

The content of `include_grader` and `include_callable` is copy-pasted in the correct section of the grader depending on the programming language.

### References in various languages

With the word reference we mean a variable that is passed to a function and the function has access to that same variable, not to a copy of it. [Here](https://en.wikipedia.org/wiki/Reference_(computer_science)) you can find a deeper explanation of the concept of reference.

Parameters passed by reference are handled as shown in each language:
* *C++* The function is declared with a parameter passed by reference using the character '&' before the parameter name. In the case of arrays, they are not passed by reference as they are already pointer.
* *C* As references are non existent in pure *C*, references are faked using pointer. So instead of passing the value to the function, a pointer to the value is passed instead. As for *C++*, nothing is done for arrays parameters as they are already passed as pointers.
* *pascal* References are declared prepending the word `var` to the parameter name.

It is important to note that in some languages passing by reference does not make a copy, instead passing normally makes a copy. This might affect performances. For example array not passed by parameters are copied in pascal and this might slow down solutions. 
