import pkg_resources
from os import unlink
from gradergen import structures
from gradergen.structures import PrimitiveType, Variable, Array, IOVariables, IOArrays, Expression
from gradergen import grader_generator
from gradergen.grader_generator import DataManager

class IoLibraryGenerator:
    def __init__(self, data):
        self.data = data
        self.read_input = ""
        self.write_input = ""
        self.read_output = ""
        self.write_output = ""

    # write line
    def write_line(self, line = "", tabulation = 0):
        self.io_library += "\t"*tabulation + line + "\n"

    # Writes a line containing: lhs = rhs
    def write_assignment(self, lhs, rhs, indentation):
        self.write_line(lhs + " = " + rhs, indentation)

    # Returns the given variables as an index of data: data["var_name"]
    @staticmethod
    def data_enclose(var_name):
        return "data[\"{0}\"]".format(var_name)

    # Converts the expression to string, but instead of using the variable
    # name it uses data["var_name"].
    @staticmethod
    def expression_to_data_string(expression):
        if expression.var is None:
            return expression.to_string()
        else:
            # A hacky way to use data["name"] instead of just name.
            var_name = expression.var.name
            expression.var.name = PythonIOLibraryGenerator.data_enclose(var_name)
            generated_string = expression.to_string()
            expression.var.name = var_name
            return generated_string

    def read_input(self):
        for input_line in self.data.input_:
            if type(input_line) == IOArrays:
                if len(input_line.arrays) == 1:
                    arr = input_line.arrays[0]
                    self.write_comment("Reading the array {0}.".format(arr.name), 1)
                    if arr.dim == 1:
                        # Reading a 1-dimensional array.
                        line_numbers.append(1)
                        self.assert_file_length(line_numbers)
                        lhs = self.data_enclose(arr.name)
                        rhs = "ReadArrayLine(\"{0}\", {1}, f[{2}])"\
                            .format(arr.type.value,
                                    self.expression_to_data_string(arr.sizes[0]),
                                    self.array_sum(line_numbers[:-1]))
                        self.write_assignment(lhs, rhs, 1)
                    else:
                        # Reading a multi-dimensional array.
                        line_sizes = map(self.expression_to_data_string, arr.sizes[:-1])
                        line_numbers.append(" * ".join("({0})".format(size) for size in line_sizes))
                        self.assert_file_length(line_numbers)
                        self.write_assignment("current_line", self.array_sum(line_numbers[:-1]), 1)
                        for i in range(len(arr.sizes) - 1):
                            current_size = self.expression_to_data_string(arr.sizes[i])
                            lhs = self.data_enclose(arr.name) + self.array_indexes(i)
                            rhs = "[None] * {0}".format(current_size)
                            self.write_assignment(lhs, rhs, 1 + i)

                            self.write_line("for {0} in range({1}):"\
                                .format(self.iteration_var(i), current_size),
                                            1 + i)
                        lhs = self.data_enclose(arr.name) + self.array_indexes(len(arr.sizes) - 1)
                        rhs = "ReadArrayLine(\"{0}\", {1}, f[current_line])"\
                            .format(arr.type.value,
                                    self.expression_to_data_string(arr.sizes[-1]))
                        self.write_assignment(lhs, rhs, len(arr.sizes))
                        self.write_line("current_line += 1", len(arr.sizes))
                else:
                    for arr in input_line.arrays:
                        # Do something
                        pass
            elif type(input_line) == IOVariables:
                if len(input_line.variables) == 1:
                    self.write_comment("Reading the variable {0}.".format(input_line.variables[0].name), 1)
                else:
                    self.write_comment("Reading the variables {0}.".format(", ".join(var.name for var in input_line.variables)), 1)
                line_numbers.append(1)
                self.assert_file_length(line_numbers)

                var_names = [self.data_enclose(var.name) for var in input_line.variables]
                var_types = ["\"{0}\"".format(var.type.value) for var in input_line.variables]
                lhs = ", ".join(var_names)
                rhs = "ReadVariablesLine(({0}), f[{1}])"\
                    .format(", ".join(var_types),
                            self.array_sum(line_numbers[:-1]))
                self.write_assignment(lhs, rhs, 1)

            self.write_line("", 1)

        self.write_line("return data", 1)

    def write(self, filename, source):
        # Unlink is used to avoid following symlink
        try:
            unlink(filename)
        except OSError:
            pass

        with open(filename, "w") as f:
            f.write(source)


# Testing. TODEL
dm = DataManager()
dm.add_variable(Variable({"name": "N", "type": PrimitiveType.INT}))
dm.add_variable(Variable({"name": "M", "type": PrimitiveType.INT}))
dm.get_variable("N").known = True
dm.get_variable("M").known = True
dm.add_variable(Array({"name": "edges", "type": PrimitiveType.REAL, "sizes": [{"variable": "M"}]}, dm))
dm.add_variable(Array({"name": "quad", "type": PrimitiveType.LONGINT, "sizes": [{"variable": "N"}, {"variable": "M"}]}, dm))

dm.input_ = [IOVariables({"variables": ["N", "M"]}, dm, "input"),
             IOArrays({"arrays": [{"name": "edges"}]}, dm, "input"),
             IOArrays({"arrays": [{"name": "quad"}]}, dm, "input")]

io_parser = PythonIOLibraryGenerator(dm)

io_parser.read_input()
print(io_parser.io_library)

