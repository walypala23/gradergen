import pkg_resources
from os import unlink
from gradergen import structures
from gradergen.structures import PrimitiveType, Variable, Array, IOVariables, IOArrays, Expression
from gradergen import grader_generator
# from gradergen.grader_generator import DataManager # TODEL

class IOLibraryGenerator:
    def __init__(self, data):
        self.data = data
        self.io_lib = ""

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
            expression.var.name = IOLibraryGenerator.data_enclose(var_name)
            generated_string = expression.to_string()
            expression.var.name = var_name
            return generated_string

    # Converts the PrimitiveType to a string enclosed in "".
    @staticmethod
    def type_to_string(primitive_type):
        return "\"" + primitive_type.value + "\""

    # Joins all the lines in a single string (separating them with \n) and
    # indents them all by 4 spaces.
    @staticmethod
    def join_and_indent(lines):
        return "\n".join(["    " + line for line in lines])

    @staticmethod
    def write(filename, source):
        # Unlink is used to avoid following symlink
        try:
            unlink(filename)
        except OSError:
            pass

        with open(filename, "w") as f:
            f.write(source)

    def generate_read_function(self, file_format):
        generated_lines = []
        for line in file_format:
            if type(line) == IOArrays:
                arrays = line.arrays
                lhs = ", ".join(
                    [self.data_enclose(arr.name) for arr in arrays])
                rhs = "read_arrays([{types}], [{sizes}], f)".format(
                    types = ", ".join(
                        [self.type_to_string(arr.type) for arr in arrays]),
                    sizes = ", ".join(
                        [self.expression_to_data_string(size) \
                            for size in arrays[0].sizes])
                )
                generated_lines.append(lhs + " = " + rhs)
            elif type(line) == IOVariables:
                variables = line.variables
                lhs = ", ".join(
                    [self.data_enclose(var.name) for var in variables])
                rhs = "read_variables([{types}], f)".format(
                    types = ", ".join(
                        [self.type_to_string(var.type) for var in variables])
                )
                generated_lines.append(lhs + " = " + rhs)
        return self.join_and_indent(generated_lines)

    def generate_write_function(self, file_format):
        generated_lines = []
        for line in file_format:
            if type(line) == IOArrays:
                arrays = line.arrays
                # write_arrays(arr_types, sizes, arrs, f)
                new_line = "write_arrays([{types}], [{sizes}], [{values}], f)".format(
                    types = ", ".join(
                        [self.type_to_string(arr.type) for arr in arrays]),
                    sizes = ", ".join(
                        [self.expression_to_data_string(size) \
                            for size in arrays[0].sizes]),
                    values = ", ".join(
                        [self.data_enclose(arr.name) for arr in arrays])
                )
                generated_lines.append(new_line)
            elif type(line) == IOVariables:
                variables = line.variables
                new_line = "write_variables([{types}], [{values}], f)".format(
                    types = ", ".join(
                        [self.type_to_string(var.type) for var in variables]),
                    values = ", ".join(
                        [self.data_enclose(var.name) for var in variables])
                )
                generated_lines.append(new_line)
        return self.join_and_indent(generated_lines)

    def generate_io_lib(self):
        with open(pkg_resources.resource_filename("gradergen.iolibgen", "problem_io_template.py.tmpl")) as template_file:
            template = template_file.read()
        self.io_lib = template.format(
            gradergen_io_lib = self.data["gradergen_io_lib_package"],
            read_input = self.generate_read_function(self.data["input"]),
            write_input = self.generate_write_function(self.data["input"]),
            read_output = self.generate_read_function(self.data["output"]),
            write_output = self.generate_write_function(self.data["output"]),
        )

    def write_io_lib(self):
        self.generate_io_lib()
        self.write(self.data["problem_io_filename"], self.io_lib)


# Testing. TODEL
# dm = DataManager()
# dm.add_variable(Variable({"name": "N", "type": PrimitiveType.INT}))
# dm.add_variable(Variable({"name": "M", "type": PrimitiveType.INT}))
# dm.add_variable(Variable({"name": "res", "type": PrimitiveType.LONGINT}))
# dm.get_variable("N").known = True
# dm.get_variable("M").known = True
# dm.get_variable("res").known = True
# dm.add_variable(Array({"name": "edges", "type": PrimitiveType.REAL, "sizes": [{"variable": "M"}]}, dm))
# dm.add_variable(Array({"name": "quad", "type": PrimitiveType.LONGINT, "sizes": [{"variable": "N"}, {"variable": "M"}]}, dm))

# dm.input_ = [IOVariables({"variables": ["N", "M"]}, dm, "input"),
             # IOArrays({"arrays": [{"name": "edges"}]}, dm, "input"),
             # IOArrays({"arrays": [{"name": "quad"}]}, dm, "input")]

# dm.output = [IOVariables({"variables": ["res"]}, dm, "output")]

# io_lib_generator = IOLibraryGenerator({
    # **dm.make_copy(),
    # "gradergen_io_lib_package": "gradergen_io_lib",
    # "problem_io_filename": "exampleproblem" + "_io.py",
# })

# io_lib_generator.write_io_lib()
