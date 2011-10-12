#!/usr/bin/python
#
import os
import sys
import code 

import argparse

import searchlib

def display(result):
    from pprint import pprint
    pprint(result)


class ParamException(Exception):
    pass

def parse_command_line():
    """
    Parses command line options and returns an argparse instance.
    """
    parser = argparse.ArgumentParser(description='Searches the D&D Insider '
            'Compendium for the keywords provided.')
    parser.add_argument('-i', '--interact', dest='interact', default=False,
            action='store_true',
            help='After running the query start the python interpreter.')
    parser.add_argument('-c', '--category', dest='category', default='Power',
            choices=searchlib.VALID_CATEGORIES, metavar='category',
            help='The category to keyward search in.  Choices: %(choices)s.  '
                    'Default: %(default)s.')
    parser.add_argument('-n', '--nameonly', dest='name_only', default=False,
            action='store_true',
            help='Only return results whose names match the keywords you '
                    'provide.')
    parser.add_argument('keywords', nargs='+',
            help='Keywords to search against the Compendium with.')
    arg_manager = parser.parse_args()
    return arg_manager

LAST_RESULT = None
def main(arg_manager):
    global LAST_RESULT

    result = searchlib.search_compendium(keywords=arg_manager.keywords,
        category=arg_manager.category, name_only=str(arg_manager.name_only),)
    display(result)
    LAST_RESULT = result
    return True

if __name__ == '__main__':
    arg_manager = parse_command_line()
    main(arg_manager)
    if arg_manager.interact:
        code.interact(local=locals())
