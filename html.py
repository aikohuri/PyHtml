# -*- coding: utf-8 -*-
import os
from htmltags import *

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


class COMMENT(TagBase):
    '''
    The comment tag is used to insert a comment in the source code.
    A comment will be ignored by the browser. You can use comments to explain
    your code, which can help you when you edit the source code at a later date.
    You can also store program-specific information inside comments.

    In this case they will not be visible for the user, but they are still
    available to the program. A good practice is to comment the text inside
    scripts and style elements to prevent older browsers, that do not support
    scripting or styles, from showing it as plain text.
    '''
    def __init__(self, *comments):
        TagBase.__init__(self, "", *comments, stag='<!--', etag='-->', emptyTag=False)


class DOCTYPE(TagBase):
    '''
    The doctype declaration should be the very first thing in an HTML document,
    before the <html> tag.

    The doctype declaration is not an HTML tag; it is an instruction to the web
    browser about what version of the markup language the page is written in.

    The doctype declaration refers to a Document Type Definition (DTD). The DTD
    specifies the rules for the markup language, so that the browsers render
    the content correctly.
    '''
    def __init__(self, DTD):
        TagBase.__init__(self, "", DTD, stag='<!DOCTYPE ', etag='>', emptyTag=False)


class PHP(TagBase):

    def __init__(self, *codes):
        '''
        codes - [stuple of str] php codes.
        '''
        TagBase.__init__(self, "", *codes, stag='<?php ', etag='?>', emptyTag=False)


class Page:

    def __init__(self, head=None, body=None, html=None, DTD=XHTML1_0_TRANSITIONAL, XMLNS="http://www.w3.org/1999/xhtml", DIR='', LANG=''):
        if head is not None and not isinstance(head, HEAD):
            raise TypeError('Invalid type: head must be an instance of HEAD class.')
        elif body is not None and not isinstance(body, BODY):
            raise TypeError('Invalid type: body must be an instance of BODY class.')

        self.doctype = DOCTYPE(DTD)
        if html is None:
            self.head = HEAD() if head is None else head 
            self.body = BODY() if body is None else body
            self.html = HTML(self.head, self.body, XMLNS=XMLNS, DIR=DIR, LANG=LANG)
        else:
            self.html = html
            self.head = None
            self.body = None

            for i, tag in enumerate(self.html.contents):
                if isinstance(tag, HEAD):
                    self.head = tag
                    self.html.contents[i] = self.head
                elif isinstance(tag, BODY):
                    self.body = tag
                    self.html.contents[i] = self.body

            if self.head is None:
                raise TypeError('a head object does not contain a HEAD object')
            elif self.body is None:
                raise TypeError('a body object does not contain a BODY object')

    def __str__(self):
        return self.toString()

    def setDoctype(self, doctype):
        '''
        Set <!DOCTYPE> tag.

        doctype - [Doctype]
        '''
        if not isinstance(doctype, Doctype):
            raise TypeError('Invalid type: doctype must be an instance of Doctype class.')

        self.doctype = doctype

    def setHtml(self, html):
        '''
        Set <HTML> tag.

        html - [HTML]
        '''
        if not isinstance(html, HTML):
            raise TypeError('Invalid type: html must be an instance of HTML class.')

        self.html = html
        self.head = None
        self.body = None

        for i, tag in enumerate(self.html.contents):
            if isinstance(tag, HEAD):
                self.head = tag
            elif isinstance(tag, BODY):
                self.body = tag

        if self.head is None:
            raise TypeError('a head object does not contain a HEAD object')
        elif self.body is None:
            raise TypeError('a body object does not contain a BODY object')

    def setHead(self, head):
        '''
        Set <HEAD> tag.

        head - [HEAD]
        '''
        if not isinstance(head, HEAD):
            raise TypeError('Invalid type: head must be an instance of HEAD class.')

        for i, tag in enumerate(self.html.contents):
            if isinstance(tag, HEAD):
                self.head = head
                self.html.contents[i] = self.head
                break

    def setBody(self, body):
        '''
        Set <BODY> tag.

        body - [BODY]
        '''
        if not isinstance(body, BODY):
            raise TypeError('Invalid type: body must be an instance of BODY class.')

        for i, tag in enumerate(self.html.contents):
            if isinstance(tag, BODY):
                self.body = body
                self.html.contents[i] = self.body
                break

    def getHtml(self):
        return self.html

    def getHead(self):
        return self.head

    def getBody(self):
        return self.body

    def toString(self, uppercase=True):
        return ''.join([self.doctype.toString(uppercase),
                        self.html.toString(uppercase)])

    def toPrettyString(self, indentChar='    ', offset='', uppercase=True):
        return '\n'.join([self.doctype.toString(uppercase),
                          self.html.toPrettyString(indentChar, offset, uppercase)])

    def save(self, filePath, indentChar='', offset='', uppercase=True):
        dir = os.path.split(filePath)[0]
        if dir and not os.path.exists(dir):
            os.makedirs(dir)

        with open(filePath, 'w') as f:
            if indentChar:
                page = self.toPrettyString(indentChar, offset, uppercase)
            else:
                page = self.toString(uppercase)
            f.write(page)



if __name__ == '__main__':
    head = HEAD()
    head.add(META(NAME="description", CONTENT="Test page"))
    head.add(META(NAME="keywords", CONTENT="HTML, CSS"))
    head.add(LINK(REL='stylesheet', TYPE='text/css', HREF='test.css'))

    body = BODY()
    body.add(H1(P('test page')))
    body.add(A('test', HREF="test.html"))
    body.contents[-1].setAttr(ONMOUSEOVER="this.style.background='pink';", ONMOUSEOUT="this.style.background='white';")
    body.add(TABLE(TR(TD('test1', STYLE="background:blue;"), TD(A('test2', HREF='test.html')), TD(STRONG('test3'))),
                   TR(TD('hello'), TD('world'), TD('!'), BGCOLOR='red'),
                   BGCOLOR='rgb(125,0,0)',
                   CLASS='table'))

    tbl = TABLE(*(TR(*(TD('(%d,%d)' % (i,j)) for j in range(10))) for i in range(10)))
    for i, row in enumerate(tbl.contents):
        row.setAttr(ONMOUSEOVER="this.style.background='rgb(%d,%d,%d)';" % (i*20,i*20,i*20), ONMOUSEOUT="this.style.background='white';")
    tbl.setAttr(ONMOUSEOVER="this.style.background='pink';", ONMOUSEOUT="this.style.background='white';")
    body.add(tbl)

    body.add(SCRIPT('document.write("Hello World!")', TYPE="text/javascript"))
    body.add(PHP('echo "Hello World";'))
    print
    print body
    print

    page = Page(head, body)
    print 
    print page.toPrettyString(indentChar='   ', offset='   ', uppercase=False)
    print
    page.save('test.html', indentChar='   ')


    html = HTML(COMMENT('Header'),
                HEAD(),
                COMMENT('Body'),
                BODY())
    html.setAttr(LANG='jp', DIR='ltr')
    print
    print html.toString(uppercase=False)
    print
    page2 = Page(html=html)
    page2.save('test2.html', indentChar='    ')
    page2.setHead(head)
    page2.setBody(body)
    page2.save('test3.html', indentChar='    ')

