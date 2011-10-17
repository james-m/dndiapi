#!/usr/bin/python
#
import os
import sys
import code 

import argparse

import searchlib

# OUTPUT functions
#
class DisplayerBase(object):
    CATEGORY = None
    FORMAT   = () 
    
    def display(self, rows):
        fmt, morphs = self._format()
        # HEADER row
        #
        hdr = {}
        for name, _, _ in self.FORMAT:
            hdr[name] = name.upper()
        self.output(hdr, fmt)
        # RESULT rows
        #
        for row in rows:
            row = self.mutate(row, morphs)
            self.output(row, fmt)

    def mutate(self, row, morphs):
        morphed = row.copy() 
        for name, morph_name in morphs.items():
            morpher = getattr(self, morph_name)
            morphed[name] = morpher(row[name])
        return morphed 
        
    def output(self, row, fmt):
        print fmt % row

    def _format(self):
        fmt = [] 
        morphs = {}
        for name, size, morph in self.FORMAT:
            fmt.append('%%(%s)%ss' % (name, size))
            if morph is None:
                continue
            morphs[name] = morph
        fmt = ' '.join(fmt)
        return fmt, morphs

DISPLAYERS = {}
class DisplayPower(DisplayerBase):
    CATEGORY = searchlib.CATEGORY_POWER
    FORMAT = [
        ('id',         20, None),
        ('name',       35, '_morph_name'), 
        ('classname',  35, None), 
        ('level',       6, None), 
        ('actiontype', 13, '_morph_actiontype'), 
        ]

    # morphs
    def _morph_actiontype(self, atype):
        if atype == 'Immediate Interrupt':
            return 'Imm. Int.'
        elif atype == 'Immediate Reaction':
            return 'Imm. Reac.'
        return atype

    def _morph_name(self, name):
        return name.replace('[Attack Technique]', '[Att. Tech.]')
DISPLAYERS[DisplayPower.CATEGORY] = DisplayPower()

class DisplayFeat(DisplayerBase):
    CATEGORY = searchlib.CATEGORY_FEAT
    FORMAT   = [
        ('id',         20, None),
        ('name',       35, None),
        ('tiername',   10, None),
       ]
DISPLAYERS[DisplayFeat.CATEGORY] = DisplayFeat()

def display(result, category):
    displayer = DISPLAYERS.get(category)
    if displayer is None:
        print 'unable to lookup displayer for category %s' % category
        return None
    displayer.display(result['rows'])

    # TOTALS
    #
    totals = {}
    for name, value in result['totals'].items():
        totals[name[:3]] = value
    print TOTALS_DISPLAY % totals

TOTALS_DISPLAY = """
 Background: %(Bac)7s             Feat: %(Fea)7s        Power: %(Pow)7s
      Class: %(Cla)7s         Glossary: %(Glo)7s         Race: %(Rac)7s
  Companion: %(Com)7s             Item: %(Ite)7s       Ritual: %(Rit)7s
      Deity: %(Dei)7s          Monster: %(Mon)7s      Terrain: %(Ter)7s
    Disease: %(Dis)7s       Para. Path: %(Par)7s         Trap: %(Tra)7s   
 Epic Dest.: %(Epi)7s           Poison: %(Poi)7s     
"""

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
    LAST_RESULT = result
    display(result, arg_manager.category)
    return True

if __name__ == '__main__':
    arg_manager = parse_command_line()
    main(arg_manager)
    if arg_manager.interact:
        code.interact(local=locals())
