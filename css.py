import os
import copy
import operator

import html


class Rule:

    def __init__(self, sels='', decls={}):
        '''
        sels - [str/list] selector(s) for the style rule.
        decls - [dict] declaractions of the style rule.
        '''
        if isinstance(sels, list):
            self.selectors = set(sels)
        elif sels:
            self.selectors = set([sels])
        else:
            self.selectors = set()
        self.declarations = decls
        self.rules = {
                'inside' : (' ', set()),
                'below'  : ('>', set()),
                'after'  : ('+', set()),
                'behind' : ('~', set()),
                }

    def __str__(self):
        return self.toPrettyString()

    def add(self, *args):
        '''
        Add declaration(s) to this rule.
        args - [dict] declarations
             - [str, str] a pair of property name and property value
        '''
        if len(args) == 1 and isinstance(args[0], dict):
            self.declarations.update(args[0])
        elif len(args) > 1 and all([isinstance(a, str) for a in args]):
            for i in range(0, len(args), 2):
                self.declarations[args[i]] = args[i+1]
        return self

    def inside(self, *args):
        '''
        Add Rules inside this rule. (i.e. elem elem)
        args - [Rule]
        '''
        if any([not isinstance(a, Rule) for a in args]):
            raise Exception('*** Must be Rule object ***')
        self.rules['inside'][1].update(args)
        return self

    def below(self, *args):
        '''
        Add Rules below this rule. (i.e. elem>elem)
        args - [Rule]
        '''
        if any([not isinstance(a, Rule) for a in args]):
            raise Exception('*** Must be Rule object ***')
        self.rules['below'][1].update(args)
        return self

    def after(self, *args):
        '''
        Add Rules after this rule. (i.e. elem+elem)
        args - [Rule]
        '''
        if any([not isinstance(a, Rule) for a in args]):
            raise Exception('*** Must be Rule object ***')
        self.rules['after'][1].update(args)
        return self

    def behind(self, *args):
        '''
        Add Rules behind this rule. (i.e. elem~elem)
        args - [Rule]
        '''
        if any([not isinstance(a, Rule) for a in args]):
            raise Exception('*** Must be Rule object ***')
        self.rules['behind'][1].update(args)
        return self

    def addSelector(self, *sels):
        '''
        *sels - [str] selector(s) of the style rule.
        '''
        if len(sels) == 1 and isinstance(sels[0], set):
            self.selectors.update(sels[0])
        else:
            self.selectors.update(sels)
        return self

    def getSelector(self):
        return self.selectors

    def getDeclration(self):
        return self.declarations

    def merge(self, iRule):
        '''
        Merge the selector and declarations of iRule into this rule.
        '''
        self.addSelector(iRule.selectors)
        self.add(iRule.declarations)
        for key, (_, rules) in iRule.rules.items():
            self.rules[key][1].update(rules)
        return self

    def _getFirstSelName(self):
        return '' if not self.selectors else sorted([s for s in self.selectors])[0]

    def _toString(self, iParentSel=[], relation=' '):
        if iParentSel:
            iParentSel = ['%s%s%s' % (ps, relation, ss) for ps in iParentSel for ss in self.selectors]
        else:
            iParentSel = copy.deepcopy(self.selectors) # deep copy

        iParentSel = sorted(iParentSel)

        css = []
        if self.declarations:
            css.append(''.join([','.join(iParentSel),
                                '{' if iParentSel else '',
                                ''.join(['%s:%s;' % (k,v) for k,v in sorted(self.declarations.items(), key=operator.itemgetter(0))]),
                                '}' if iParentSel else '']))
        for key, (rel, rules) in self.rules.items():
            css.extend([rule._toString(iParentSel, rel) for rule in sorted(rules, key=lambda rule: rule._getFirstSelName())])

        return ''.join(css)

    def toString(self, uppercase=True):
        return self._toString()

    def _toPrettyString(self, iIndentChar='    ', iOffset='', iParentSel=[], relation=' '):
        if iParentSel:
            iParentSel = ['%s%s%s' % (ps, relation, ss) for ps in iParentSel for ss in self.selectors]
        else:
            iParentSel = copy.deepcopy(self.selectors) # deep copy

        iParentSel = sorted(iParentSel)

        css = []
        if self.declarations:
            css.append('\n'.join(['%s%s' % (iOffset, ',\n'.join(iParentSel)),
                                  '%s{' % (iOffset) if iParentSel else '',
                                  '\n'.join(['%s%s%s: %s;' % (iOffset, iIndentChar,k,v) for k,v in sorted(self.declarations.items(), key=operator.itemgetter(0))]),
                                  '%s}' % iOffset if iParentSel else ''])) 
        for key, (rel, rules) in self.rules.items():
            css.extend([rule._toPrettyString(iIndentChar, iOffset, iParentSel, rel) for rule in sorted(rules, key=lambda rule: rule._getFirstSelName())])

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
                ).inside(
                Rule('li',
                     {'padding':'0.4em',
                      'margin':'0.8em 0 0.8em'},
                     ).below(
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

    print '--------------------------------------------'

    rule_h3 = Rule('h3', {'font-size':'1.2em'})
    rule.after(rule_h3)
    print rule

    print '--------------------------------------------'

    rule_p  = Rule('p', {'padding':'0.3em'})
    rule.merge(rule_p)
    print rule

    css.add(rule)
    css.save('test.css', iIndentChar='    ')

    print css.toStyleTag()
    print
    print linkTag('test.css')

