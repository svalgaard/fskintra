# -*- coding: utf-8 -*-

import schildren
import config
import surllib
import semail
import json

MAX_CACHE_AGE = .99


def docFindDocuments(cname, rootTitle, bs, title):
    folder = rootTitle
    if title:
        folder += u' / ' + title.replace(u'>', u'/')

    docs = bs.findAll('div', 'sk-document')
    config.clog(cname, u'%s: %d dokumenter fundet ' %
                (folder, len(docs)))

    for doc in docs:
        docTitle = doc.find('span', 'sk-documents-document-title').text.strip()
        docDate = doc.find('div', 'sk-documents-date-column').text.strip()
        a = doc.find('a')
        url = a and a['href'] or ''
        if '.' in docTitle:
            sfn = docTitle.rsplit(u'.', 1)[0]
        else:
            sfn = docTitle

        if docTitle and docDate and url:
            # Create HTML snippet
            html = u"<p>Nyt dokument: <span></span> / <b></b></p>\n"
            html += u"<!-- Sidst opdateret: %s -->" % docDate
            h = surllib.beautify(html)
            h.span.string = folder
            h.b.string = docTitle

            msg = semail.Message(cname, 'doc', unicode(h))
            msg.setTitle(sfn)
            msg.setDateTime(docDate)
            msg.addAttachment(url, docTitle)
            msg.setMessageID(url.split('/')[-1])
            msg.maybeSend()


def skoleDocuments(cname):
    for rootTitle, folder in [('Klassens dokumenter', 'class')]:
        config.clog(cname, u'%s: Kigger efter dokumenter' % rootTitle)
        url = schildren.getChildURL(cname, '/documents/' + folder)

        bs = surllib.skoleGetURL(url, True, MAX_CACHE_AGE)
        docFindDocuments(cname, rootTitle, bs, '')

        # look for sub folders
        js = bs.find(id='FoldersJson')
        if js and js.has_attr('value'):
            sfs = json.loads(js['value'])

            for sf in sfs:
                if sf[u'Name'].startswith('$'):
                    continue

                title = sf[u'Title']
                url = sf[u'Url']
                bs = surllib.skoleGetURL(url, True, MAX_CACHE_AGE, None, True)

                docFindDocuments(cname, rootTitle, bs, title)
