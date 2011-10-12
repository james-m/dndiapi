'''API for executing searches against the DNDI search compandium.'''

import urlparse
import urllib
import urllib2
import BeautifulSoup

# DEFINE some of the url endpoints to hit
#
BASE_URL  = 'http://www.wizards.com/dndinsider/compendium/compendiumsearch.asmx/'
SRCH_URL  = urlparse.urljoin(BASE_URL, 'KeywordSearch')
XSRCH_URL = urlparse.urljoin(BASE_URL, 'KeywordSearchWithFilters')

# these are the valid entries for the "tab" GET parameter. not sure if it's
# case-sensitive. Wouldn't be surprised if it is.
#
VALID_CATEGORIES = (
    'Race', 
    'Class', 
    'Power', 
    'Feat', 
    'Item', 
    'Skill', 
    'Ritual', 
    'ParagonPath', 
    'EpicDestiny', 
    'Monster', 
    'Deity', 
    'Glossary')
VALID_NAME_ONLY = (
    'True', 
    'False', 
    )

class InvalidCategory(Exception):
    pass

def _makeurl(url, keywords, category, name_only = 'False'):
    # just in case
    #
    name_only = str(name_only)
    if name_only not in VALID_NAME_ONLY:
        raise ValueError('invalid name only spec %r' % name_only)

    if category not in VALID_CATEGORIES:
        raise InvalidCategory('invalid category %s' % category)

    data = {
        'keywords' : keywords, 
        'nameOnly' : name_only, 
        'tab'      : category, 
        } 
    return '%s?%s' % (url, urllib.urlencode(data))


class HTTPError(Exception):
    pass

def search_compendium(keywords, category, name_only='False'):
    '''Non-filters search

    keywords: a text string to search
    category: The category to search. See VALID_CATEGORIES for valid categories. 
    name_only: string 'True' or 'False', the default. Not quite sure what it means
        exactly but has something to with only the name (brilliant!)

    raises:
        httplib2.HTTPError: when there's a problem.
    '''
    result = _httpsearch(keywords, category, name_only)
    return parse_full(result)

def _httpsearch(keywords, category, name_only):
     # build the endpoint
    #
    s_url = _makeurl(
        SRCH_URL, keywords, category = category, name_only = name_only)

    # fetch the page, brute force read for now
    #
    # TODO: lots of error handling around making http requests
    result = urllib2.urlopen(s_url).read()
    return result


class ParseException(Exception):
    pass

def parse_full(xml):
    '''given the xml returned from a comp search, try an iterrupt 
    the returned data from a search query.
    '''
    soup = BeautifulSoup.BeautifulSOAP(xml)
    data = soup.find('data')
    if not data:
        raise ParseException('unable to find data element')

    totals  = data.find('totals')
    results = data.find('results')
    if not totals:
        raise ParseException('unable to find totals element')
    if not results:
        raise ParseException('unable to find results elelemtn')

    # totals
    #
    by_category = {}
    for tab in totals.findAll('tab'):
        table_name = tab.find('table').text
        count = int(tab.find('total').text)
        by_category[table_name] = count

    # results. since we're not exactly sure what's coming back (other then
    # inspecting the category the query was made with) lets just be better at
    # handling stuff
    #
    result_rows = []
    for child in results.childGenerator():
        if not isinstance(child, BeautifulSoup.Tag):
            continue
        result_rows.append(_soupdict(child))

    return {
        'totals'  : by_category, 
        'results' : result_rows, 
        }

def _soupdict(tag):
    '''given a beautifulsoup tag turn into a python dictionary. 

    the tag needs to be relatively shallow. This method will only 
    turn attributes and the children into dictionary keys. 
    the tag needs to be relatively shallow. This method will only 
    turn attributes and the children into dictionary keys. 

    so for example:
    
    <root attr_a="val_a">
        <child_b>val_cb</child_b>
        <child_c>val_cc</child_c>
    </root>
    
    will result in:
    {'_type' : 'root', 
     'attr_a'  : 'val_a', 
     'child_b' : 'val_cb', 
     'child_c' : 'val_cc', 
     }
    '''
    data = {
        '_type' : tag.name, 
        }
    for name, value in tag.attrs:
        try:
            value = int(value)
        except:
            pass
        data.update({name: value})
    return data
