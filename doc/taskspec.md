
# Grader specifier file (`task.spec`)

The grader specification file (usually called `task.spec`) is the file which contains the information needed to generate graders (and templates). Not exactly *all* of the information, as we will see, but the vast majority.

This file should always be present in a subdirectory of gradergen's working directory (or at the path specified using the flag `--taskspec`). The name of the file is not enforced, but it is suggested to call it `task.spec` (or, at least, to use the `.spec` extension).

## General notions on the syntax

The specification file follows a strict syntax to describe how the grader should read/write and interact with the contestant's program.

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
doTheThing(int N, char x[], char y[], int &result1, int &result2)

***input***
# Comments can be anywhere in the files, not only at the beginning!
N
x[] y[]

***calls***
doTheThing(N, x, y, result1, result2)

***output***
result1 result2
```

To see further examples of valid `task.spec` we suggest you to watch in the `testing/` folder. However, be aware that some of the tests (a couple of them) are there to test for errors, so the `task.spec` might not be valid.

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

Everything about the type identifier and the name is exactly as it is for [primitive type variables](#primitive-type-variables), so we suggest to look there for further details. The sizes have to be expressions, for details about expressions see the [appriopriate section](#expressions). The dimension of the array (the number of sizes) is not limited, even if multidimensional array are not supported in every language.

The line states that the variable with name `array_name` is a multidimensional array with sizes `size1`, `size2`, ..., `sizeN` and its primitive type is the given one.

## Prototypes
In this section you have to declare all the prototypes of the function that will be called by the grader.
Here you have to insert both the functions that should be defined in the contestant source code and those that are defined in the `include_grader` file. For further details about `include_grader` see the [proper section](#the-include_grader-and-include_callable-files).   
This is the only part of `task.spec` processed to generate the template.

Each line of this section must contain a prototype for a function. The general syntax of the prototype is:
```
return_type function_name(parameter1, parameter2, ..., parameterN)
```
The `return_type` is a type_specifier and obviously is the type of the variable returned by the function.  
After the prototype, on the same line, there might be `{location}` where location can be `grader` or `solution`. If it is `grader` it means that this prototype is defined in `include_grader` and should not be present in the template. The default is `solution`, that means that this function has to be defined in the contestant's code.  

Each parameter must contain the type (arrays are possible), the name (used in the template and in the function declaration in the grader) and whether the parameters should be passed by reference or not. If you want to know more about references see the [section](#references-in-various-languages) focused on them. A parameter should be passed by reference only if the function is expected to modify it.   
The syntax for the parameter definition is the following:
```
type_identifier &parameter_name[][]..[][]
```
The ampersand `&`, if present, means that the parameter should be passed by reference. The sequence of `[]`, if present, means that the parameter is an array and its dimension is the number of pairs of square brackets.

Given all of the information above you should now understand the meanings of the following correct prototypes:
```
# FindSum returns the sum of a and b
int FindSum(int a, int b)
```

```
# This function is defined in the grader and calls N times the function 'int  
# approximate(double)' defined by the contestant. On each call, heights[i] is  
# passed to approximate and the return value is stored in solutions[i].
CallManyTimes(int N, real heights[], int &solutions[]) {grader}
```

```
# This function returns the minimum cut relative to the vertices source and sink in 
# graph passed in the parameters.
longint MinCut(int N, int E, int source, int sink, int from[], int to[], int weight[])
```

## Input
This is the section where you should insert the description of the structure of the input to be read by the grader.  
Each line describes a part of the input (not necessarily a single line of the input file) and the order of the lines reflects the order in which each part
is present in the input file.
Each line can be of two different kinds: it can be related to simple variables or to arrays. We will focus separately on the two different kinds:

#### Variables input line
The syntax is very easy in this case, it is just a sequence of variables' names separated by spaces. The semantic meaning is as obvious as it should be; namely, it means that those variables are present on the same line, in the given order, in the input file. The primitive types of the variables do not have to be the same.

Here is the code needed to describe a line that contains two variables, one named `alpha` and the other named `height`:
```
alpha height
```

#### Arrays input line
The syntax is very similar to [the one just described](#variables-input-line) but the corresponding structure of the input is more complex.
The only difference in the syntax is that arrays' names should be followed by the correct amount of `[]`, indicating their sizes. The number of `[]` is not really processed by `gradergen` (even though an error will be raised if you don't put them) and is just for the user to have a clear view of how the input should look like just reading the `input` section in `task.spec`.  
As an example the following is a valid line:
```
A[][][] B[][][] long_array_name123[][][]
```

All arrays on the same line of the input section should have exactly the same sizes, therefore if one of the arrays is declared as `int A[N][N]` and another one is declared as `int B[N][M]` an error will be raised. As you will see, it would not make sense to put arrays of different sizes on the same line. However there is no constraint on the types of the arrays.

The complicated part is the meaning of the line (i.e. the corresponding part in the input file), that varies with the number of arrays involved, with their sizes and even with their types.
We will go through the three possible cases in this punctured list:

* *Only one array of type `char`*: It is treated as a string (or as an array of strings) and printed accordingly. If the array `A` has sizes `size1, size2, ..., sizen`, in the input there will be `size1*size2*...*size(n-1)` lines each containing a string of length `sizen`.  
The array is read as you would expect, the second character of the first string of the input corresponds to `A[0]...[0][1]`. If for example `A` has dimension 1 and size N, the input will contain a single line with a string of N characters and this string is exactly what `A` should be.
* *Only one array of type non-`char`*: This is treated like a normal list. Everything is exactly as for strings (described above) apart from the fact that single entries are separated by a space. An additional space is also present at the end of each line.
Let's assume for example that `A` has type `int`, dimension two and sizes NxM. Then the input will contain N lines, each with M integers separated by spaces.
* *More than one array*: Let's name the sizes of the arrays `size1, size2, ..., sizen`. The input will contain `size1*size2*...*sizen` lines, each with as many values as the number of arrays involved. All the values on the same line are separated by a space (without a trailing space).  
Each line is mapped to an entry in all the arrays, and it is done exactly as you would guess.
For example the second value on the second line is mapped to the entry `[0]...[0][1]` of the second array of the list.
So if you have two arrays with dimension 1 and length N, the input will have N lines and each line will contain two values.

## Calls
The calls section contains all the calls the grader should do at runtime.
Each line refers to a single call and the order of the lines it's the same as the order in which the functions will be called.

The syntax of a single call line is as follows:
```
return_var = function_name(parameter1, parameter2, ..., parameterN)
```
where the `function_name` must be the name of a function declared in the `prototypes` section and the parameters' names and `return_var` are relative to variables declared in the `variables` section.  
The first part (`return_var = `) can be absent if the function is not returning anything (i.e. if the prototype has empty type).  
The parameters do *not* have to specify whether they should be passed by reference, their own type or whether they are arrays or not. All of that is deduced from the prototype. Of course the prototype have not only to match the name of the function but the types of all the variables involved (parameters and `return_var`) too. The name of the parameters don't have to be the same in the prototype declaration and in the call.

For instance, if the variables `result` and `N` and the array `numbers` have been declared, and there is a prototype called `sum` which matches all the parameters, then 
```
result = sum(N, numbers)
```
is a correct call.

## Output
Everything (both the syntax and the corresponding structure of the file) is exactly as in the `input` section, so see the [input documentation](#input).

## Appendix

### Type's identifiers

The type's identifiers are the following ones:

* `int`: A simple integer (32 bit).
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
74
-7*variable_name+134
100000
```

### The `include_grader` and `include_callable` files
These two files contain additional source code to be included in the grader. The reason for their existence is to enrich the capability of the generated graders and make possible to use `gradergen` also for *complex* problems that are not fully expressed by the strict syntax of `task.spec`.  
These files have to be called `include_grader.lang_extension` and `include_callable.lang_extension`, where `lang_extension` is the proper extension of the programming language. If you want `gradergen` to use them they have to be in the same directory as `task.spec` or in the directory specified with the flag `--include_dir`.   
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

* `include_callable`: This one contains all the functions that the contestant's program can call (not the declarations of the function but the whole implementations). These functions can interact with all the variables defined in the grader. Moreover in this file you can also, accordingly to the language, define new variables. We strongly advise not to do any input or output in this section as IO is handled differently if fast input is enabled or not.  
For example, `include_callable` must be used in problems where the contestant's program can ask questions and the final score depends on the number of questions asked. Here it is a correct `include_callable` handling queries and keeping the number of queries asked:

```C++
bool IsBiggerThanSecretNumber(int n) {
	number_of_queries++;
	return n > secret_number;
}
```

The content of `include_grader` and `include_callable` is copy-pasted in the correct section of the grader depending on the programming language.

### References in various languages

With the word reference we mean a variable that is passed to a function and the function has access to that same variable, not to a copy of it. [Here](https://en.wikipedia.org/wiki/Reference_(computer_science)) you can find a deeper explanation of the concept of reference.

Parameters passed by reference are handled as shown in each language:
* *C++*: The function is declared with a parameter passed by reference using the character '&' before the parameter name. In the case of arrays, they are not passed by reference as they are already pointers.
* *C*: As references are non existent in pure *C*, references are faked using pointers. So instead of passing the value to the function, a pointer to the value is passed instead. As for *C++*, nothing is done for arrays parameters as they are already passed as pointers.
* *pascal*: References are declared prepending the word `var` to the parameter name.

It is important to note that in some languages passing by reference does not make a copy, while passing by value does. This might affect performances. For example arrays not passed by reference are copied in pascal and this might slow down solutions. 
