import mechanize
import cookielib
import BeautifulSoup
from searchlib import VALID_CATEGORIES

class InvalidLookup(Exception):
    pass

class CompendiumProxy(object):
    """
    Handles connecting & authenticating with the DDI Compendium as well as
    looking up full data inside the Compendium.
    """
    BASE_URL = 'http://www.wizards.com/dndinsider/compendium'
    LOOKUP_URL = BASE_URL + '/display.aspx?page=%s&id=%d'
    PAGES = [x.lower() for x in VALID_CATEGORIES]

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.browser = mechanize.Browser(factory=mechanize.RobustFactory())
        self.browser.set_cookiejar(cookielib.LWPCookieJar())

    def lookup(self, page, object_id):
        """
        Handles looking up data for a given page type & id.
        """
        if page not in self.PAGES:
            raise InvalidLookup('%s not a valid page type.' % (page,))
        response = self.browser.open(self.LOOKUP_URL % (page, object_id))
        # Check to see if form1 has a password field.  If not, then we're
        # authenticated already and we got the data we were looking for.  If so
        # then we need to auth.
        self.browser.select_form('form1')
        try:
            self.browser.form['email'] = self.email
            self.browser.form['password'] = self.password
        except mechanize._form.ControlNotFoundError:
            # We're already authenticated, return the data
            return response.read()
        # We're not authenticated, so authenticate and then return the data
        response = self.browser.submit()
        return response.read()

# Ok, parsing the returned HTML is going to SUUUUUUUUUUUUUUUCK
# Here's some code that I played with that at least works with epicdestinies:
# b = BeautifulSoup.BeautifulSoup(response)
# detail = b.findAll('div', id='detail')
# 
# After that you have to parse through detail, which is mostly free-form html
# and not really meant to be easily parseable.  What's worse, we'd likely have
# to write a different parser for each of the different page types.
#
# LAME
