#
# -*- encoding: utf-8 -*-
#

import re
import config
import surllib
import semail
import mechanize

URL_PREFIX = '/Infoweb/Fi/Dokumentarkiv/'
URL_MAIN   = URL_PREFIX + 'Dokliste.asp'
# /Infoweb/Fi/Dokumentarkiv/VisDokument.asp?Id=6816

def docFindDocuments(bs):

    # Find title
    # "Dokumentarkiv for 1C"
    maintitle = bs.h2.text

    lines = bs.findAll('tr', 'linje1') + bs.findAll('tr', 'linje2')

    for line in lines:
        # One file type
        fts = line.findAll('td', width='1%')
        assert(len(fts) == 1 and fts[0].img) # excatly one file type image link
        i = fts[0].img['src']
        extension = u'.' + i.split('/')[-1][2:-4].lower()

        # One document
        ahs = line.findAll('td', width='58%')
        assert(len(ahs) == 1 and ahs[0].text and ahs[0].a['href']) # exactly one title + link
        href = ahs[0].a['href']
        title = unicode(ahs[0].text)

        # find Date
        dts = line.findAll('td', width='18%')
        assert(len(dts) == 1 and dts[0].text) # exactly one date
        date = unicode(dts[0].text)

        # Create HTML snippet
        h = surllib.beautify(u"<p>Nyt dokument: <a href=''>%s</a></p>" % title)
        h.a['href'] = URL_PREFIX + href
        h.a['usefilename'] = title + extension
        
        msg = semail.Message('documents', h)
        msg.setTitle(u'%s (%s)' % (title, maintitle))
        msg.setDate(date)
        print msg
        msg.send()
        # semail.maybeEmail(msg)


def skoleDocuments():
    global URL_MAIN, bs

    config.log(u'Kigger efter nye dokumenter')
    url = 'http://%s%s' % (config.HOSTNAME, URL_MAIN)
        
    # read the initial page
    bs = surllib.skoleGetURL(url, True) # FIXME set nocache=true
    docFindDocuments(bs)

if __name__ == '__main__':
    # test
    skoleDocuments()
