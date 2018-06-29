# -*- coding: utf-8 -*-

import schildren
import config
import surllib
import semail
import json


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
            html = u"<p>Nyt dokument: <i/> / <b><i/></b>"
            html += u"<br/>Sidst opdateret: <i/></p>"
            h = surllib.beautify(html)
            h.i.replaceWith(folder)
            h.i.replaceWith(docTitle)
            h.i.replaceWith(docDate)

            msg = semail.Message(u'doc', unicode(h))
            msg.setTitle(sfn)
            msg.setDateTime(docDate)
            msg.addAttachment(url, docTitle)
            msg.addChild(cname)
            msg.maybeSend()


def skoleDocuments(cname):
    for rootTitle, folder in [('Klassens dokumenter', 'class')]:
        config.clog(cname, u'%s: Kigger efter dokumenter' % rootTitle)
        url = schildren.getChildURL(cname, '/documents/' + folder)

        bs = surllib.skoleGetURL(url, True, True)
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
                bs = surllib.skoleGetURL(url, True, True, None, True)

                docFindDocuments(cname, rootTitle, bs, title)


if __name__ == '__main__':
    # test
    skoleDocuments()
