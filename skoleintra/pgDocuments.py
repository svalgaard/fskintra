# -*- coding: utf-8 -*-

import re
import config
import surllib
import semail
import datetime
import urllib

URL_PREFIX = 'http://%s/Infoweb/Fi/Dokumentarkiv/' % config.HOSTNAME
URL_MAIN = URL_PREFIX + 'Dokliste.asp'
URL_DOC = URL_PREFIX + 'VisDokument.asp?Id='


def docFindDocuments(bs, foldername='Dokumentarkiv'):
    '''Input beatifulsoup with content from a page of documents
    Looks at this and all subfolders, and sends any new messages'''

    trs = bs.findAll('tr')

    for line in trs:
        if not line.has_key('class'):
            continue
        if not [c for c in line['class'].split() if c.startswith('linje')]:
            continue

        links = line.findAll('a')
        assert(len(links) >= 2)

        # find file type
        ext = links[0].img['src'].split('/')[-1][2:-4].lower()

        # find name of file
        title = links[1].text
        ltitle = foldername + ' / ' + title

        # find url
        url = links[0]['href']
        config.log(u'Kigger på dokument url: %s' % url, 3)
        m = re.match(r"javascript:visdokument\((\d+),'([^']+)'\).*", url)
        if m:
            url = m.group(2)
        elif 'visdokument' in url.lower():
            url = URL_DOC + re.search('.*?(\d+)', links[0]['href']).group(1)
        elif links[0].has_key('onclick') and 'visdok' in links[0]['onclick']:
            url = url  # href is actually the file url
        else:
            assert('Dokliste' in url)
        url = urllib.quote(url.encode('iso-8859-1'), safe=':/?=&%')

        # find date
        dts = line.findAll('td', width='18%')
        assert(len(dts) == 1 and dts[0].text)  # exactly one date
        date = dts[0].text

        # now do stuff
        if 'Dokliste' in url:
            # this is a subfolder

            # first look at (potentially cached version)
            suburl = URL_PREFIX + url
            subbs = surllib.skoleGetURL(suburl, True)

            subdate = datetime.date(*reversed(map(int, date.split('-'))))
            if subbs.cachedate <= subdate or subbs.cacheage >= 1.9:
                # cached version is too old - refetch
                subbs = surllib.skoleGetURL(suburl, True, True)
                config.log(u'Kigger på folderen %s' % title)
            else:
                config.log(u'Kigger på folderen %s (fra cache)' % title)

            docFindDocuments(subbs, ltitle)
        else:
            # this is an actual document
            config.log(u'Kigger på dokumentet %s' % ltitle)

            # Create HTML snippet
            html = u"<p>Nyt dokument: <a href=''>%s</a></p>" % ltitle
            h = surllib.beautify(html)
            h.a['href'] = url
            h.a['usefilename'] = title + '.' + ext

            msg = semail.Message('documents', h)
            msg.setTitle(u'%s' % title)
            msg.setDate(date)
            msg.maybeSend()


def skoleDocuments():
    global bs

    # surllib.skoleLogin()
    config.log(u'Kigger efter nye dokumenter')

    # read the initial page
    bs = surllib.skoleGetURL(URL_MAIN, True, True)
    docFindDocuments(bs)

if __name__ == '__main__':
    # test
    skoleDocuments()
