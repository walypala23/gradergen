#!/usr/bin/env python3

import nome_sorgente_contestant_io

data = nome_sorgente_contestant_io.read_input("input.txt")
nome_sorgente_contestant_io.write_input(data, "iolibgen_input.txt")
nome_sorgente_contestant_io.read_output(data, "c.out")
nome_sorgente_contestant_io.write_output(data, "iolibgen_output.txt")
