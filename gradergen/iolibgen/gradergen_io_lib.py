#!/usr/bin/env python3
import math
from sys import stdin, stdout

# BEGIN READING UTILITY FUNCTIONS

# Returns a variable of type primitive_type (or similar if python doesn't have
# such a type) parsed from the given string.
# Raises an error if the string is malformed.
def from_string_to_type(primitive_type, string):
    if primitive_type is "longint":
        res = int(string)
        MAX_LONG_INT = 2**63 - 1
        assert(-MAX_LONG_INT <= res <= MAX_LONG_INT)
    if primitive_type is "int":
        res = int(string)
        MAX_INT = 2**31 - 1
        assert(-MAX_INT <= res <= MAX_INT)
    if primitive_type is "char":
        res = str(string)
        assert(len(res) == 1)
    if primitive_type is "real":
        res = float(string)
        assert(not math.isnan(res))
    return res
        
# Returns a tuple containing the variable parsed from the line.
# The var_types is a list of the types of the variables contained in the line.
# An error is raised if the line is malformed. 
def read_variables_line(var_types, line):
    splitted_line = line.split()
    assert(len(splitted_line) == len(var_types))
    return tuple(from_string_to_type(var_types[i], splitted_line[i]) \
                     for i in range(len(var_types)))

# Returns a list parsed from the line.
# The array_type is the type of the elements in the array, the length is the
# expected length of the array.
# An error is raised if the line is malformed. 
def read_array_line(array_type, length, line):
    # The line is splitted by spaces unless it contains a string.
    if array_type == "char":
        splitted_line = list(line)
    else:
        splitted_line = line.split()
    assert(len(splitted_line) == length)

    return [from_string_to_type(array_type, el) for el in splitted_line]

def safe_readline(f):
    line = f.readline()
    assert(line)
    return line.rstrip("\n")

# Recursively reads arrays from the file and fills the arrs_to_fill
# parameter.
# If the arrs to be read are two and each of them is one-dimensional with
# size N, the arrs_to_fill parameter must be of the form 2xN (and sizes must be
# [N]).
def internal_read_arrays(array_types, sizes, f, arrs_to_fill):
    size = sizes[0]
    if len(sizes) == 1:
        if len(array_types) == 1:
            partial_res = read_array_line(array_types[0], size, safe_readline(f))
            for i in range(size):
                arrs_to_fill[0][i] = partial_res[i]
        else:
            for i in range(size):
                partial_res = read_variables_line(array_types, safe_readline(f))
                for t in range(len(arrs_to_fill)):
                    arrs_to_fill[t][i] = partial_res[t]
    else:
        for i in range(size):
            internal_read_arrays(array_types, sizes[1:], f,
                                 [arr[i] for arr in arrs_to_fill])

# Returns a multidimensional arrays with the specified sizes.
def construct_multidimensional_array(sizes):
    size = sizes[0]
    if len(sizes) == 1:
        return [0]*size
    else:
        return [construct_multidimensional_array(sizes[1:]) \
                    for _ in range(size)]

# END READING UTILITY FUNCTIONS

# BEGIN PUBLIC READING API

# Open the given file in read mode.
# If the filename is None, stdin is returned.
def open_to_read(filename):
    if filename is not None:
        return open(filename, "r")
    else:
        return stdin

# Reads a single line of the file containing variables with types as specified
# in var_types.
def read_variables(var_types, f):
    return read_variables_line(var_types, safe_readline(f))

# Reads one or multiple lines of the file containing arrays with types and
# sizes as specified by the parameters.
def read_arrays(array_types, sizes, f):
    arrs_to_fill = construct_multidimensional_array([len(array_types)] + sizes)
    internal_read_arrays(array_types, sizes, f, arrs_to_fill)
    return arrs_to_fill

# Asserts that the file f is at end of file.
def assert_eof(f):
    assert(f.readline() == "")

# END PUBLIC READING API

# BEGIN WRITING UTILITY FUNCTIONS

def convert_to_string(primitive_type, value):
    if primitive_type == "real":
        return "{0:0.6f}".format(value)
    return str(value)

# Returns a line containing the given values separated by a space.
def write_variables_line(var_types, values):
    line = " ".join([convert_to_string(var_types[i], values[i]) \
                        for i in range(len(var_types))])
    return line

# Returns a line containing all the entries of the array separated by a space.
def write_array_line(arr_type, arr):
    separator = "" if arr_type == "char" else " "

    # Here we add a trailing space to be consistent with the graders.
    # Even if in python is not a issue, avoiding adding the extra space
    # in C/C++ would make the grader less readable.
    line = "".join([convert_to_string(arr_type, el) + separator for el in arr])
    return line

# END WRITING UTILITY FUNCTIONS

# BEGIN WRITING PUBLIC API

# Open the given file in write mode.
# If the filename is None, stdout is returned.
def open_to_write(filename):
    if filename is not None:
        return open(filename, "w")
    else:
        return stdout

# Writes a single line of the file containing variables with types and values
# as specified in the parameters.
def write_variables(var_types, values, f):
    print(write_variables_line(var_types, values), file=f)

# Writes one or multiple lines of the file containing arrays with types, sizes
# and values as specified by the parameters.
def write_arrays(arr_types, sizes, arrs, f):
    size = sizes[0]
    if len(sizes) == 1:
        if len(arrs) == 1:
            print(write_array_line(arr_types[0], arrs[0]), file=f)
        else:
            for i in range(size):
                print(write_variables_line(arr_types, [arr[i] for arr in arrs]),
                      file=f)
    else:
        for i in range(size):
            write_arrays(arr_types, sizes[1:], [arr[i] for arr in arrs], f)

# END WRITING PUBLIC API
