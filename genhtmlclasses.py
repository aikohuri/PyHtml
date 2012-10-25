import re
import httplib
import sys
import datetime


def parseTable(data):
    s = data.find('<table')
    data = data[s:]
    t = data.find('</table>')
    data = data[:t]

    table = []
    #
    # get header
    #
    header = re.findall(r'<th[^>]*>([^<]*)</th>', data)
    table.append(tuple(header))

    while data:
        idx = data.find('<tr')
        if idx == -1:
            break
        data = data[idx+len('<tr>'):]

        row = []
        for i in range(len(header)):
            s = data.find('<td')
            t = data.find('</td>')
            col = re.findall(r'>([^<]+)<', data[s:t+len('</td>')])
            row.append([re.sub(r' {2,}', ' ', c.replace('\r',' ').replace('\n',' ').replace('\t',' ')).strip() for c in col if c.strip()])
            data = data[t+len('</td>'):]
        table.append(tuple(row))

    return table

def getAttr(data, attrName):
    idx = data.find(attrName)
    if idx < 0:
        return []
    table = parseTable(data[idx:])
    attrList = []
    if len(table[0]) == 3:
        for name, val, desc in table[1:]:
            if len(name) > 1 and name[1] == 'New':
                desc.insert(0, 'New in HTML5.')
            attrList.append((name[0].replace(':', '__').replace('-','_').upper(),
                             val,
                             ' '.join(desc)
                             ))
    elif len(table[0]) == 2:
        for name, desc in table[1:]:
            if len(name) > 1 and name[1] == 'New':
                desc.insert(0, 'New in HTML5.')
            attrList.append((name[0].replace(':', '__').replace('-','_').upper(),
                             ' '.join(desc)
                             ))
    else:
        raise Exception('unknown table format')

    #print attrName
    #for a in attrList:
    #    print a
    #print
    return attrList

def getDefinition(data):
    s = data.find('<h2>Definition and Usage</h2>')
    if s < 0:
        raise Exception('cannot find "Definition and Usage"')
    data = data[s+len('<h2>Definition and Usage</h2>'):]
    t = data.find('<hr>')
    if t < 0:
        raise Exception('cannot find "<hr>"')
    data = data[:t]
    
    lines = []
    line = ''
    for item in re.findall(r'>([^<]+)<', data):
        item = re.sub(r' {2,}', ' ', item.replace('\r',' ').replace('\n',' ').replace('\t',' ')).strip()
        if not item and line:
            lines.append(line)
            line = ''
            continue
        line = item if not line else '%s %s' % (line, item)
    if line:
        lines.append(line)
    return lines

def getTips(data):
    s = data.find('<h2>Tips and Notes</h2>')
    if s < 0:
        return []
    data = data[s+len('<h2>Tips and Notes</h2>'):]
    t = data.find('<hr>')
    if t < 0:
        raise Exception('cannot find "<hr>"')
    data = data[:t]

    tips = []
    tip = ''
    for item in re.findall(r'>([^<]+)<', data):
        item = re.sub(r' {2,}', ' ', item.replace('\r',' ').replace('\n',' ').replace('\t',' ')).strip()
        if not item:
            continue
        if 'Tip:' in item or 'Note:' in item:
            if tip:
                tips.append(tip)
            tip = item
        else:
            tip = '%s %s' % (tip, item)
    if tip:
        tips.append(tip)

    return tips

def getBrowserSupport(data):
    s = data.find('<h2>Browser Support</h2>')
    data = data[s:]
    t = data.find('<hr>')
    data = data[:t]
    return data.find('Explorer') != -1, data.find('Firefox') != -1, data.find('Opera') != -1, data.find('Google') != -1, data.find('Safari') != -1

def getHtmlSupport(data):
    s = data.find('<h2>Differences Between HTML 4.01 and HTML5</h2>')
    if s < 0:
        return ''
    data = data[s+len('<h2>Differences Between HTML 4.01 and HTML5</h2>'):]
    t = data.find('<hr>')
    if t < 0:
        raise Exception('cannot find "<hr>"')
    data = data[:t]

    defList = re.findall(r'>([^<]+)<', data)
    defList = [d.replace('\r',' ').replace('\n',' ').replace('\t',' ') for d in defList if d.strip()]
    return ' '.join([re.sub(r' {2,}', ' ', d.replace('\r',' ').replace('\n',' ').replace('\t',' ')).strip() for d in defList])

def getTagList(conn):
    data = getPageData(conn, '/tags/default.asp')
    idx = data.find('HTML</span> Tags')
    t = data[idx:].find('</div>')
    data = data[idx+len('HTML</span> Tags'):idx+t]
    return re.findall(r'href\="([^"]+)"[^;]+;(\w+)', data)

def getTagForm(conn):
    data = getPageData(conn, '/tags/ref_html_dtd.asp')
    s = data.find('<h2>HTML/XHTML Elements and Valid DTDs</h2>')
    data = data[s+len('<h2>HTML/XHTML Elements and Valid DTDs</h2>'):]
    t = data.find('</table>')
    data = data[:t]
    return re.findall(r'<tr>[^<]*<td[^<]+<a[^;]+;([^&]+)&gt;', data)

def getGlobalAttr(conn):
    data = getPageData(conn, '/tags/ref_standardattributes.asp')
    return getAttr(data, '<h2>HTML Global Attributes</h2>')

def getEventAttrs(conn):
    data = getPageData(conn, '/tags/ref_eventattributes.asp')
    eventAttrs = {}
    eventAttrs['window'   ] = getAttr(data, '<h2>Window Event Attributes</h2>')
    eventAttrs['form'     ] = getAttr(data, '<h2>Form Events</h2>')
    eventAttrs['keyboard' ] = getAttr(data, '<h2>Keyboard Events</h2>')
    eventAttrs['mouse'    ] = getAttr(data, '<h2>Mouse Events</h2>')
    eventAttrs['media'    ] = getAttr(data, '<h2>Media Events</h2>')
    return eventAttrs

def getPageData(conn, addr):
    print 'Requesting %s ...' % addr,
    conn.request('GET', addr)
    resp = conn.getresponse()
    print resp.status, resp.reason
    return resp.read().replace('&nbsp;',' ').replace('&quot;','"')

def getTagInfo(conn, tagPage):
    data = getPageData(conn, '/tags/%s' % tagPage)
    info = {}
    info['tagdef'         ] = getDefinition(data)
    info['browserSupport' ] = getBrowserSupport(data)
    info['tips'           ] = getTips(data)
    info['htmlSupport'    ] = getHtmlSupport(data)
    info['attrs'          ] = getAttr(data, '<h2>Attributes</h2>')
    info['requiredAttrs'  ] = getAttr(data, '<h2>Required Attributes</h2>')
    info['optionalAttrs'  ] = getAttr(data, '<h2>Optional Attributes</h2>')
    info['standardAttrs'  ] = getAttr(data, '<h2>Standard Attributes</h2>')
    info['globalAttrs'] = False
    s = data.find('<h2>Global Attributes</h2>')
    if s >= 0:
        t = data[s:].find('<hr>')
        if t >= 0 and data[s:s+t].find('tag also supports') >= 0:
            info['globalAttrs'] = True

    info['eventAttrs'] = False
    s = data.find('<h2>Event Attributes</h2>')
    if s >= 0:
        t = data[s:].find('<hr>')
        if t >= 0:
            if data[s:s+t].find('tag also supports') >= 0:
                info['eventAttrs'] = True
            elif data[s:s+t].find('tag supports the following event attributes') >= 0:
                info['eventAttrs'] = getAttr(data, '<h2>Event Attributes</h2>')
    return info

def genPyClass(tag, isEmptyTag, globalAttrs, eventAttrs, tagInfo):
    allAttrs = [a[0] for a in tagInfo['attrs']]
    allAttrs.extend([a[0] for a in tagInfo['requiredAttrs']])
    allAttrs.extend([a[0] for a in tagInfo['optionalAttrs']])
    allAttrs.extend([a[0] for a in tagInfo['standardAttrs']])

    if tagInfo['globalAttrs']:
        allAttrs.extend([a[0] for a in globalAttrs])

    if tagInfo['eventAttrs']:
        if tagInfo['eventAttrs'] == True:
            for key, val in eventAttrs.items():
                allAttrs.extend([a[0] for a in val])
        else:
            allAttrs.extend([a[0] for a in tagInfo['eventAttrs']])

    definitionStr = '\n'.join([
        '\t[Definition and Usage]',
        '%s' % '\n'.join(['\t\t%s' % d for d in tagInfo['tagdef']])
        ])

    browserSupportStr = '\n'.join([
        '\t[Browser Support]',
        '\t\t%s' % ', '.join([browser for browser, support in zip(['IE', 'Firefox', 'Opera', 'Chrome', 'Safari'], tagInfo['browserSupport']) if support
        ])])

    htmlSupportStr = ''
    if tagInfo['htmlSupport']:
        htmlSupportStr = '\n'.join([
            '\t[Differences Between HTML 4.01 and HTML5]',
            '\t\t%s' % tagInfo['htmlSupport'],
            ])

    tipsStr = ''
    if tagInfo['tips']:
        tipsStr = '\n'.join([
            '\t[Tips and Notes]',
            '\n'.join(['\t\t%s' % s for s in tagInfo['tips']]),
            ])

    attrStr = ''
    if tagInfo['attrs']:
        attrStr = '\n'.join([
            '\t\t[Attributes]',
            ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                               ','.join(type),
                                               desc
                                               ) for attr, type, desc in tagInfo['attrs']])
            ])

    reqAttrStr = ''
    if tagInfo['requiredAttrs']:
        reqAttrStr = '\n'.join([
            '\t\t[Required Attributes]:',
            ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                               ','.join(type),
                                               desc
                                               ) for attr, type, desc in tagInfo['requiredAttrs']])
            ])

    optAttrStr = ''
    if tagInfo['optionalAttrs']:
        optAttrStr = '\n'.join([
            '\t\t[Optional Attributes]:',
            ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                               ','.join(type),
                                               desc
                                               ) for attr, type, desc in tagInfo['optionalAttrs']])
            ])

    stdAttrStr = ''
    if tagInfo['standardAttrs']:
        stdAttrStr = '\n'.join([
            '\t\t[Standard Attributes]:',
            ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                               ','.join(type),
                                               desc
                                               ) for attr, type, desc in tagInfo['standardAttrs']])
            ])

    if not tagInfo['globalAttrs']:
        glbAttrStr = ''
    else:
        glbAttrStr = '\n'.join([
            '\t\t[Global Attributes]:',
            ''.join(['\t\t\t%s - %s\n' % (attr, desc) for attr, desc in globalAttrs])
            ])

    if not tagInfo['eventAttrs']:
        evtAttrStr = ''
    elif tagInfo['eventAttrs'] == True:
        evtAttrStr = '\n'.join([
            '\t\t[Event Attributes]:',
            ''.join(['\t\t%s Events:\n%s' % (key,
                                             ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                                                                ','.join(type),
                                                                                desc
                                                                                ) for attr, type, desc in attrs])
                                             ) for key, attrs in eventAttrs.items()]),
            ])
    else:
        evtAttrStr = '\n'.join([
            '\t\t[Event Attributes]:',
            ''.join(['\t\t\t%s - [%s] %s\n' % (attr,
                                               ','.join(type),
                                               desc
                                               ) for attr, type, desc in tagInfo['eventAttrs']])
            ])

    data = ['class %s(TagBase):' % tag.upper(),
            "\t'''",
            definitionStr,
            browserSupportStr,
            htmlSupportStr,
            tipsStr,
            "\t'''",
            '\tdef __init__(self%s%s):' % ('' if isEmptyTag else ', *contents',
                                           ', **attrs' if allAttrs else ''
                                           ),
            '\t\t"""',
            '%s%s' % ('' if isEmptyTag else '\t\t*contents - [tuple] tag contents.\n',
                     '\t\t**attrs - [dict] tag attributes.\n' if allAttrs else ''
                     ),
            attrStr,
            reqAttrStr,
            optAttrStr,
            stdAttrStr,
            glbAttrStr,
            evtAttrStr,
            '\t\t"""',
            '\t\tTagBase.__init__(self, "%s"%s, emptyTag=%s)' % (tag.upper(),
                                                                 '' if isEmptyTag else ', *contents',
                                                                 isEmptyTag
                                                                 ),
            '' if not allAttrs else '%s\n%s' % ('\t\tself.attrset = frozenset([%s])' % ','.join(['"%s"' % a for a in allAttrs]),
                                                '\t\tself.setAttr(**attrs)'
                                                ),
            '\n\n',
            ]
    
    return '\n'.join([d for d in data if d])

def main():
    if len(sys.argv) != 2:
        print
        print '%s <output_filename>' % sys.argv[0]
        print
        sys.exit(1)

    fname = sys.argv[1]

    conn = httplib.HTTPConnection('www.w3schools.com')

    tagList       = getTagList(conn)
    tagFormList   = getTagForm(conn)
    emptyTagFlags = [True if not tag in tagFormList else False for _, tag in tagList]

    globalAttrs   = getGlobalAttr(conn)
    eventAttrs    = getEventAttrs(conn)

    f = open(fname, 'w')

    cmt = [
    '"""',
    '%s' % datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
    'This file was auto-generated by genhtmlclasses.py',
    '"""',
    ''
    ]

    f.write('\n'.join(cmt))
    f.write('from htmltagbase import TagBase\n\n\n')

    for (link, tag), isEmptyTag in zip(tagList, emptyTagFlags):
        print '----------------------------------------'
        print 'parsing <%s> tag' % tag

        tagInfo = getTagInfo(conn, link)

        if tag == 'h1':
            for i in range(1, 7):
                tag = 'h%d' % i
                data = genPyClass(tag, isEmptyTag, globalAttrs, eventAttrs, tagInfo)
                f.write(data.replace('\t', '    '))
        else:
            data = genPyClass(tag, isEmptyTag, globalAttrs, eventAttrs, tagInfo)
            f.write(data.replace('&lt;', '<').replace('&gt;', '>').replace('\x92', "'").replace('\t', '    '))

    f.close()
    conn.close()


if __name__ == '__main__':
    main()

