"""
Common utilities, most of them useful for a Qt related project.
"""

import sys
import os
import json
import pathlib

__all__ = [
    'gen_unique_path_from',
    'overwrite_if_needed_or_exit',
    'exists_or_exit',
    'dump_objs',
]

#######################################################################
##
##   FILE RELATED UTILITIES AMONG OTHER STUFF
##
#######################################################################

def gen_unique_path_from(path_: str) -> str:
    """
    Generates a unique file path from C{path_} if the given {path_}
    exists. Otherwise, just returns that path.

    Returns a C{str} with the new unique path.

    >>> gen_unique_path_from('abc')   # assuming 'abc' exists
    abc_2
    >>> gen_unique_path_from('abc')   # assuming 'abc' doesn't exist
    abc
    >>> gen_unique_path_from('abc')   # assuming 'abc' and 'abc_2' both
    abc_3                             # exist
    """
    if not path_:
        raise ValueError('Empty path')
    path_ext = pathlib.Path(path_).suffix
    path_and_name = path_.partition(path_ext)[0] if path_ext else path_
    i = 2
    while os.path.exists(path_):
        path_ = f'{path_and_name}_{i}{path_ext}'
        i += 1
    return path_
#:

def overwrite_if_needed_or_exit(dest_file_path: str, error_code=3):
    """
    Overwrites the file given by C{dest_file} if the file exists
    and if the user wants to overwrite. Exits from Python if the file 
    exists and the user doesn't want to overwrite.
    c{error_code} is the code given to c{sys.exit}.
    """
    if os.path.exists(dest_file_path):
        answer = input(f"File {dest_file_path} exists. Overwrite (y or n)? ")
        if answer.strip().lower() != 'y':
            print("File will not be overwritten")
            sys.exit(error_code)
    #:
#:

def exists_or_exit(file_path: str, error_code=3):
    """
    The file given by {file_path} must exist or else we exit from
    Python.
    c{error_code} is the code given to c{sys.exit}.
    """
    if not os.path.exists(file_path):
        print(f"File {file_path} doesn't exist", file=sys.stderr)
        sys.exit(error_code)
    #:
#:

def dump_objs(objs_iter, dump_fn=json.dumps):
    """
    'Dumpa' um iterável de objectos do mesmo tipo para um array de 
    objectos de JSON. Recebe uma função para 'dumpar' os objectos 
    individuais. Atenção que em JSON só existe uma forma de representar 
    conjuntos de elementos: o array, que equivale a uma C{list}a em 
    Python. Assim sendo, esta função devolve um JSON-array que, à 
    semelhança de uma lista de Python, é delimitado por '[' e ']'.
    """
    return '[%s]' % ','.join((dump_fn(obj) for obj in objs_iter))
#: