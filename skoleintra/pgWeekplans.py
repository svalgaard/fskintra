#
# -*- encoding: utf-8 -*-
#

import re
import config
import surllib
import semail
import datetime
import urllib

URL_PREFIX = 'http://%s/Infoweb/Fi/' % config.HOSTNAME
URL_MAIN = URL_PREFIX + 'Ugeplaner.asp'

def docFindWeekplans(bs):

    trs = bs.findAll('tr')

    for line in trs:
        if not line.has_key('class'):
            continue
        if not [c for c in line['class'].split() if c.startswith('linje')]:
            continue

        links = line.findAll('a')
        assert(len(links) >= 1)

        # find week date
        title = links[0].text

        # find url
        url = links[0]['href']
        url = URL_PREFIX + urllib.quote(url.encode('iso-8859-1'), safe=':/?=&%')

        bs = surllib.skoleGetURL(url, True)

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
    docFindWeekplans(bs)

if __name__ == '__main__':
    # test
    skoleWeekplans()
