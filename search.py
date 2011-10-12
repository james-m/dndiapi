#!/usr/bin/python
#
import os
import sys
import code 

from optparse import OptionParser

import searchlib

USAGE = '''
usage: %prog [options] <keyword search>

Searches the D&D Insider Compandium for the keywords provided.
'''

def display(result):
    from pprint import pprint
    pprint(result)

class ParamException(Exception):
    pass

def main(options, args):
    if len(args) == 0:
        raise ParamException('Keywords required!')
    result = searchlib.search_compendium( 
        keywords = args, 
        category = options.category, 
        name_only = str(options.name_only), 
        )
    display(result)
    return 0

if __name__ == '__main__':
    op = OptionParser(USAGE)
    op.add_option(
        '-i', '--interact', 
        dest='interact', 
        help='After running the query start the python interpreter',
        action='store_true',
        default=False, 
        )
    val_cat_str = ', '.join(searchlib.VALID_CATEGORIES)
    op.add_option(
        '-c', '--category', 
        dest = 'category', 
        help = 'The category to keyword search in.'
        'Possible values incude ' + val_cat_str + '. '
        '(default: Power)',
        default = 'Power',
        )
    op.add_option(
        '-n', '--nameonly',
        dest = 'name_only', 
        help = 'Search nameOnly True (default: False)',
        action = 'store_true', 
        default = False,
        )
    
    options, args = op.parse_args()
    try:
        v = main(options, args)
    except ParamException, e:
        print 'Invalid parameters. %s' % e.args[0]
        sys.exit(1)
    if options.interact:
        code.interact(local = locals())
    sys.exit(v)
