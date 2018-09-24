# -*- coding: utf-8 -*-

import config
import sbs4
import schildren
import semail
import surllib

SECTION = 'sgn'


def findEvents(cname, bs):
    toptitle = bs.select('.sk-grid-top-header li')
    toptitle = toptitle[0].string.strip() if toptitle else u'Ukendt'

    for ul in bs.select('.sk-signup-container ul.ccl-rwgm-row'):
        if 'sk-grid-top-header' in ul['class']:
            continue   # Ignore top header
        ebs = sbs4.beautify('<p><dl></dl></p>')
        dl = ebs.dl

        key = ''
        kv, kvl = {}, []
        for li in ul.select('li'):
            # Kill a tags inside, if any
            for a in (li.findAll('a') or []):
                a.unwrap()
            s = li.text.strip()

            if 'sk-grid-inline-header' in li['class']:
                li.name = u'dt'
                li['style'] = 'font-weight:bold'
                key = s.rstrip(':')
            else:
                li.name = u'dd'
                kvl.append((key, s))
                kv[key.lower()] = s
            dl.append(li)

        if list(k for k, v in kv.items() if k.startswith(u'status') and
                v.lower().startswith(u'lukket')):
            continue  # Ignore this line

        msg = semail.Message(cname, SECTION, unicode(ebs))
        msg.setTitle(u'%s: %s' % kvl[0])
        msg.maybeSend()


@config.Section(SECTION)
def skoleSignup(cname):
    'Tilmelding til samtaler/arrangementer'
    config.clog(cname, u'Kigger efter nye samtaler/arrangementer')
    for suffix in ('conversation', 'event'):
        url = schildren.getChildURL(cname, '/signup/' + suffix)
        bs = surllib.skoleGetURL(url, True)
        findEvents(cname, bs)
