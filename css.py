import os
import copy
import operator

import html



class Rule:

    def __init__(self, sels='', decls={}, *childRules):
        '''
        sels - [str/list] selector(s) for the style rule.
        decls - [dict] declaractions of the style rule.
        *childRules - [Rule] child(ren) of this style rule.
        '''
        if isinstance(sels, list):
            self.selectors = set(sels)
        elif sels:
            self.selectors = set([sels])
        else:
            self.selectors = set()
        self.declarations = decls
        self.children = set(childRules)

    def __str__(self):
        return self.toPrettyString()

    def add(self, *args):
        '''
        args - [dict] add declaration to this rule.
               [str, str] add (prop, val) pair to declaration of this rule.
               [list] add list of Rules to this rule's children list.
               [Rule] add Rule(s) to this rule's children list.
        '''
        if len(args) == 1 and isinstance(args[0], dict):
            self.declarations.update(args[0])
        elif len(args) == 2 and all([isinstance(a, str) for a in args]):
            self.declarations[args[0]] = args[1]
        elif len(args) == 1 and isinstance(args[0], list) or all([isinstance(a, Rule) for a in args]):
            if isinstance(args[0], list):
                self.children.update(args[0])
            else:
                self.children.update(args)

    def addSelector(self, *sels):
        '''
        *sels - [str] selector(s) of the style rule.
        '''
        if len(sels) == 1 and isinstance(sels[0], set):
            self.selectors.update(sels[0])
        else:
            self.selectors.update(sels)

    def getSelector(self):
        return self.selectors

    def getDeclration(self):
        return self.declarations

    def merge(self, iRule):
        self.addSelector(iRule.selectors)
        self.add(iRule.declarations)
        self.add(iRule.children)

    def _getFirstSelName(self):
        return '' if not self.selectors else sorted([s for s in self.selectors])[0]

    def _toString(self, iParentSel=[]):
        if iParentSel:
            iParentSel = ['%s %s' % (ps, ss) for ps in iParentSel for ss in self.selectors]
        else:
            iParentSel = copy.deepcopy(self.selectors) # deep copy

        iParentSel = sorted(iParentSel)

        css = []
        if self.declarations:
            css.append(''.join([','.join(iParentSel),
                                '{' if iParentSel else '',
                                ''.join(['%s:%s;' % (k,v) for k,v in sorted(self.declarations.items(), key=operator.itemgetter(0))]),
                                '}' if iParentSel else '']))
        css.extend([child._toString(iParentSel) for child in sorted(self.children, key=lambda child: child._getFirstSelName())])

        return ''.join(css)

    def toInline(self):
        return ''.join(['%s:%s;' % (k,v) for k,v in sorted(self.declarations.items(), key=operator.itemgetter(0))])

    def toString(self, uppercase=True):
        return self._toString()

    def _toPrettyString(self, iIndentChar='    ', iOffset='', iParentSel=[]):
        if iParentSel:
            iParentSel = ['%s %s' % (ps, ss) for ps in iParentSel for ss in self.selectors]
        else:
            iParentSel = copy.deepcopy(self.selectors) # deep copy

        iParentSel = sorted(iParentSel)

        css = []
        if self.declarations:
            css.append('\n'.join(['%s%s' % (iOffset, ',\n'.join(iParentSel)),
                                  '%s{' % (iOffset) if iParentSel else '',
                                  '\n'.join(['%s%s%s: %s;' % (iOffset, iIndentChar,k,v) for k,v in sorted(self.declarations.items(), key=operator.itemgetter(0))]),
                                  '%s}' % iOffset if iParentSel else ''])) 
        css.extend([child._toPrettyString(iIndentChar, iOffset, iParentSel) for child in sorted(self.children, key=lambda child: child._getFirstSelName())])

        return '\n'.join(css)

    def toPrettyString(self, iIndentChar='    ', iOffset='', uppercase=True):
        return self._toPrettyString(iIndentChar, iOffset)


class Css:

    def __init__(self, *rules):
        '''
        *rules - [Rule] style rules.
        '''
        if not all([isinstance(r, Rule) for r in rules]):
            raise TypeError('invalid Rule object')

        self.rules = set(rules)

    def __str__(self):
        return self.toPrettyString()

    def add(self, *rules):
        '''
        *rules - [Rule] style rule(s).
        '''
        if all([isinstance(r, Rule) for r in rules]):
            self.rules.update(rules)
        else:
            raise TypeError('invalid Rule object')

    def toString(self, uppercase=True):
        return ''.join([rule.toString(uppercase) for rule in sorted(self.rules, key=lambda rule: rule._getFirstSelName())])

    def toPrettyString(self, iIndentChar='    ', iOffset='', uppercase=True):
        return '\n'.join([rule.toPrettyString(iIndentChar, iOffset, uppercase) for rule in sorted(self.rules, key=lambda rule: rule._getFirstSelName())])

    def toStyleTag(self):
        return html.STYLE(self)

    def save(self, iFilePath, iIndentChar='', iOffset='', uppercase=True):
        dir = os.path.split(iFilePath)[0]
        if dir and not os.path.exists(dir):
            os.makedirs(dir)

        with open(iFilePath, 'w') as f:
            if iIndentChar:
                f.write(self.toPrettyString(iIndentChar, iOffset, uppercase))
            else:
                f.write(self.toString(uppercase))


if __name__ == '__main__':
    def linkTag(iCssPath):
        return html.LINK(REL='stylesheet', TYPE='text/css', HREF=iCssPath)

    css = Css()

    rule = Rule(['ul#comments', 'ol#comments'],
                {'margin':'0', 'padding':'0'},
                Rule('li',
                     {'padding':'0.4em',
                      'margin':'0.8em 0 0.8em'},
                     Rule('h3', {'font-size':'1.2em'}),
                     Rule('p', {'padding':'0.3em'}),
                     Rule('p.meta', {'text-align': 'right', 'color':'#ddd'})))

    print rule.toString()
    print
    print
    print rule.toPrettyString()

    css.add(rule)

    rule = Rule('table')
    rule.add({'background':'red', 'font-size':'20px'})

    rule_h3 = Rule('h3', {'font-size':'1.2em'})
    rule.add(rule_h3)

    rule_p  = Rule('p', {'padding':'0.3em'})
    rule.merge(rule_p)

    print rule
    css.add(rule)
    css.save('test.css', iIndentChar='    ')

    print css.toStyleTag()
    print
    print linkTag('test.css')
    print Rule('',{'sewer':'vsdf'}).toInline()

