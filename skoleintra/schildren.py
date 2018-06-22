# -*- coding: utf-8 -*-

import config
import surllib
import re

NAMES_IGNORE = [u'Skolebestyrelsen', u'Kontaktforældre']

# map of children => urlPrefix
# 'Andrea 0A' => '/parent/1234/Andrea/'
_children = None


def skoleGetChildren():
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
            url = a['href'].rsplit('/', 1)[0]
            if url in seen:
                continue
            seen.add(url)
            name = a.text.strip() or fst
            if name not in _children:
                config.log(u'Barn %s => %s' % (name, url), 1)
                _children[name] = url

    ckey = lambda n: tuple(n.rsplit(' ', 1)[::-1])
    return sorted(_children.keys(), key=ckey)


def skoleSelectChild(name):
    global _children, URL_PREFIX
    assert(name in _children)

    if name == config.CHILD_NAME:
        config.log(u'[%s] er allerede valgt som barn' % name)
    else:
        config.log(u'Vælger [%s]' % name)
        config.CHILD_NAME = name
        config.CHILD_PREFIX = 'https://%s%s' % (config.HOSTNAME, _children[name])
