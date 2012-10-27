from collections import deque
from os.path import abspath, expanduser


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

    def addFromFile(self, path):
        with open(abspath(expanduser(path)), 'r') as f:
            self.contents.append(f.read())

    def set(self, *contents):
        '''
        Set the tag contents to *contents.

        *contents - [str/Tag] a content surrounded by <tag>...</tag>.
        '''
        self.contents = list(contents)

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
            contents = [c if not hasattr(c,'toString') else c.toString(uppercase) for c in self.contents if c]
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
            contents = '\n'.join(['%s%s' % (newOffset, c) if not hasattr(c,'toPrettyString') else c.toPrettyString(indentChar, newOffset, uppercase)
                                  for c in self.contents if c])
            data = ['%s%s' % (offset, self.stag) if self.stag is not None else '%s<%s%s>' % (offset, tagName, attrs),
                    '%s' % (contents),
                    '%s%s' % (offset, self.etag) if self.stag is not None else '%s</%s>' % (offset, tagName)]
            data = '\n'.join([d for d in data if d])

        return data

