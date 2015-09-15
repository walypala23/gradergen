from setuptools import setup, find_packages

setup(
    name='gradergen',
    version='0.1',
    description='Grader generator',
    packages=find_packages(exclude=['testing']),
    package_data={
        'gradergen.languages': ['fast_io.c', 'fast_io.cpp', 'fast_io.pas'],
    },
    entry_points={
        'console_scripts': [
            'gradergen=gradergen.grader_generator:main',
        ],
    },
)
