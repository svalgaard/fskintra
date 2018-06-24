# -*- coding: utf-8 -*-

import config
import surllib
import re

NAMES_IGNORE = [u'Skolebestyrelsen', u'Kontaktforældre']

# map of children => urlPrefix
# 'Andrea 0A' => '/parent/1234/Andrea/'
_children = None


def getChildren():
    '''Returns of list of "available" children in the system'''
    global _children
    if not _children:
        _children = dict()
        seen = set()

        config.log(u'Henter liste af børn')
        data = surllib.skoleLogin()

        # Name of "First child"
        fst = data.find(id="sk-personal-menu-button").text.strip()

        for a in data.findAll('a', href=re.compile('.*/Index$')):
            url = a['href'].rsplit('/', 1)[0].rstrip('/')
            if url in seen:
                continue
            seen.add(url)
            name = a.text.strip() or fst
            if name not in _children:
                config.log(u'Barn %s => %s' % (name, url), 1)
                _children[name] = url
        config.log(u'Følgende børn blev fundet: ' + u', '.join())


    ckey = lambda n: tuple(n.rsplit(' ', 1)[::-1])
    return sorted(_children.keys(), key=ckey)


def getChildURLPrefix(cname):
    getChildren()
    assert(name in _children)

    return surllib.absurl(_children[cname])
