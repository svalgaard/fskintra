#
# -*- encoding: utf-8 -*-
#

import config
import surllib

URL_PREFIX = 'http://%s/Infoweb/Fi2/' % config.HOSTNAME
URL = URL_PREFIX + 'Faneblade.asp'

# map of children => pageToSelectChild
_children = None


def skoleGetChildren():
    '''Returns of list of "available" children in the system'''
    global URL, _children

    # ensure that we are logged in
    # surllib.skoleLogin() # done automatically later

    config.log(u'Henter liste af børn')

    if not _children:
        data = surllib.skoleGetURL(URL, asSoup=True, noCache=True)

        _children = {}
        for a in data.findAll('a'):
            href = a['href']
            name = a.span.text
            _children[name] = href

    return sorted(_children.keys())


def skoleSelectChild(name):
    global _children, URL_PREFIX
    assert(name in _children)

    if name == config.CHILDNAME:
        config.log(u'[%s] er allerede valgt som barn' % name)
    else:
        config.warn(u'Vælger [%s]' % name)
        url = URL_PREFIX + _children[name]
        _ = surllib.skoleGetURL(url, False, noCache=True)
        config.CHILDNAME = name

if False:
    c = skoleGetChildren()
    print repr(_children)
    for cname in c:
        print cname
        skoleSelectChild(cname)
