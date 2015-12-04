gradergen
===========

Introduction
------------

**gradergen** is a tool meant to generate graders and templates files of olympic problems. It is designed to work well with [CMS](https://github.com/cms-dev/cms), the Contest Management System.

Dependencies
------------

Ensure that you have the `pyyaml` module installed.

Installation
------------

To install the `gradergen` command, run the following commands:

```bash
$ git clone https://github.com/walypala23/grader-creator
$ cd grader-creator
$ sudo python3 setup.py install
```

Usage
-----

Once installed, you can use the `gradergen` command like this: 

```bash
$ gradergen --task_yaml filename1 --task_spec filename1 --all
```

where `filename1` and `filename2` refers to task.yaml and task.spec, the flag --all tells that all templates and graders must be created.
If you omit --task_yaml or --task_spec they will be searched.

Instead of `--all` you can use `--stage` (with optional `fast` argument, if you want fastIO) which automatically sets all configurations as used in italian olympic stages (only C++ language is used, graders and templates are saved in att/ and sol/).
So the command line would be as simple as
```bash
$ gradergen --stage fast
```
and should be executed inside the task folder.
