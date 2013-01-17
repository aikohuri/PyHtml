from collections import deque
from os.path import abspath, expanduser


SP    = '&nbsp;'  # non-breaking space
LT    = '&lt;'    # less than
GT    = '&gt;'    # greater than
AMP   = '&amp;'   # ampersand
CENT  = '&cent;'  # cent
POUND = '&pound;' # pound
YEN   = '&yen;'   # yen
EURO  = '&euro;'  # euro
SECT  = '&sect;'  # section
COPY  = '&copy;'  # copyright
REG   = '&reg;'   # registered trademark
TRADE = '&trade;' # trademark

# This DTD contains all HTML elements and attributes, but does NOT INCLUDE
# presentational or deprecated elements (like font). Framesets are not allowed.
HTML4_01_STRICT = 'HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"'

# This DTD contains all HTML elements and attributes, INCLUDING presentational
# and deprecated elements (like font). Framesets are not allowed.
HTML4_01_TRANSITIONAL = 'HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"'

# This DTD is equal to HTML 4.01 Transitional, but allows the use of frameset
# content.
HTML4_01_FRAMESET = 'HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd"'

# This DTD contains all HTML elements and attributes, but does NOT INCLUDE
# presentational or deprecated elements (like font). Framesets are not allowed.
# The markup must also be written as well-formed XML.
XHTML1_0_STRICT = 'html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'

# This DTD contains all HTML elements and attributes, INCLUDING presentational
# and deprecated elements (like font). Framesets are not allowed. The markup 
# must also be written as well-formed XML.
XHTML1_0_TRANSITIONAL = 'html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"'

# This DTD is equal to XHTML 1.0 Transitional, but allows the use of frameset 
# content.
XHTML1_0_FRAMESET = 'html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'

# This DTD is equal to XHTML 1.0 Strict, but allows you to add modules (for 
# example to provide ruby support for East-Asian languages).
XHTML1_1 = 'html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'


class TagBase:

    def __init__(self, tagName, *contents, **kargs):
        '''
        tagName - [str] a tag name.
        *contents - [str/Tag] a tag content surrounded by <tag>...</tag>.
        **kargs - [dict]
            stag - [str] a start tag.
            etag - [str] an end tag
            emptyFlag = [bool] a flag to indicate an empty tag or not
        '''
        self.tagName = tagName
        self.contents = list(contents)
        self.stag = kargs.get('stag', None)
        self.etag = kargs.get('etag', None)
        self.emptyTag = kargs.get('emptyTag', False)
        self.attrset = frozenset()
        self.attrlist = deque()

    def __str__(self):
        return self.toString()

    def add(self, *contents):
        '''
        Add *contents to the tag contents.

        *contents - [str/Tag] a content surrounded by <tag>...</tag>.
        '''
        self.contents.extend(list(contents))
        return self

    def addFromFile(self, path):
        with open(abspath(expanduser(path)), 'r') as f:
            self.contents.append(f.read())
        return self

    def set(self, *contents):
        '''
        Set the tag contents to *contents.

        *contents - [str/Tag] a content surrounded by <tag>...</tag>.
        '''
        self.contents = list(contents)
        return self

    def setAttr(self, **attrs):
        '''
        **attrs - [dict] tag attributes (ex. class, name, src, xmlLang, etc)
        '''
        for attr, val in attrs.items():
            if attr in self.attrset:
                setattr(self, attr, val)
                self.attrlist.append(attr)
            else:
                raise TypeError('<%s> does not have "%s" attribute' % (self.tagName, attr))
        return self

    def toString(self, uppercase=True):
        if uppercase:
            attrs = ' '.join(['%s="%s"' % (a.replace('__',':').replace('_','-'), getattr(self, a)) for a in self.attrlist])
            tagName = self.tagName
        else:
            attrs = ' '.join(['%s="%s"' % (a.replace('__',':').replace('_','-').lower(), getattr(self, a)) for a in self.attrlist])
            tagName = self.tagName.lower()

        if attrs:
            attrs = ''.join([' ', attrs])

        if self.emptyTag:
            data = '%s%s%s' % (self.stag if self.stag is not None else '<%s' % (tagName),
                               attrs,
                               self.etag if self.etag is not None else ' />')
        else:
            contents = [c.replace('<',LT).replace('>',GT) if not hasattr(c,'toString') else c.toString(uppercase) for c in self.contents if c]
            contents = ''.join(contents)

            data = [self.stag if self.stag is not None else '<%s%s>' % (tagName, attrs),
                    contents,
                    self.etag if self.etag is not None else '</%s>' % tagName]
            data = ''.join([d for d in data if d])

        return data

    def toPrettyString(self, indentChar='    ', offset='', uppercase=True):
        if uppercase:
            attrs = ' '.join(['%s="%s"' % (a.replace('__',':').replace('_','-'), getattr(self, a)) for a in self.attrlist])
            tagName = self.tagName
        else:
            attrs = ' '.join(['%s="%s"' % (a.replace('__',':').replace('_','-').lower(), getattr(self, a)) for a in self.attrlist])
            tagName = self.tagName.lower()

        if attrs:
            attrs = ''.join([' ', attrs])

        if self.emptyTag:
            data = '%s<%s%s />' % (offset, tagName, attrs)
        else:
            newOffset = ''.join([offset, indentChar])
            contents = '\n'.join(['%s%s' % (newOffset, c.replace('<',LT).replace('>',GT)) if not hasattr(c,'toPrettyString') else c.toPrettyString(indentChar, newOffset, uppercase)
                                  for c in self.contents if c])
            data = ['%s%s' % (offset, self.stag) if self.stag is not None else '%s<%s%s>' % (offset, tagName, attrs),
                    '%s' % (contents),
                    '%s%s' % (offset, self.etag) if self.stag is not None else '%s</%s>' % (offset, tagName)]
            data = '\n'.join([d for d in data if d])

        return data

