#
# -*- encoding: utf-8 -*-
#
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from . import config
from . import surllib
from . import semail
import urllib.request, urllib.parse, urllib.error

URL_PREFIX = 'http://%s/Infoweb/Fi/' % config.HOSTNAME
URL_MAIN = URL_PREFIX + 'Ugeplaner.asp'


def wpTrimPlan(bs):
    '''Trim HTML to only contain title + main table'''
    b = surllib.beautify('')
    title = bs.find('h2')
    b.append(title)

    maint = [t for t in bs.findAll('table') if len(t.findAll('tr')) > 2][0]
    b.append(maint)

    return b


def wpFindWeekplans(bs):
    trs = bs.findAll('tr')

    for line in trs:
        if 'class' not in line:
            continue
        if not [c for c in line['class'].split() if c.startswith('linje')]:
            continue

        links = line.findAll('a')
        assert(len(links) >= 1)

        # find week date
        title = links[0].text

        # find url
        url = links[0]['href']
        url = url.encode('iso-8859-1')
        url = URL_PREFIX + urllib.parse.quote(url, safe=':/?=&%')

        bs = surllib.skoleGetURL(url, True)
        bs = wpTrimPlan(bs)

        msg = semail.Message('weekplans', bs)
        msg.setTitle(u'%s' % title)
        msg.updatePersonDate()
        msg.maybeSend()


def skoleWeekplans():
    global bs

    # surllib.skoleLogin()
    config.log(u'Kigger efter nye ugeplaner')

    # read the initial page
    bs = surllib.skoleGetURL(URL_MAIN, True, True)
    wpFindWeekplans(bs)

if __name__ == '__main__':
    # test
    skoleWeekplans()
