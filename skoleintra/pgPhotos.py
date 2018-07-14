# -*- coding: utf-8 -*-

import config
import schildren
import semail
import surllib

MAX_CACHE_AGE = .99


def findPhotosInFolder(cname, bs):
    title = bs.h2.text.strip()
    photos = []

    for img in bs.select('img'):
        if not img.has_attr('src'):
            continue
        url = surllib.absurl(img['src'])

        photos.append(url)

    ptext = u'%d billeder' % len(photos) if len(photos) != 1 else '1 billede'

    config.clog(cname, u'Billeder: %s: %s' % (title, ptext))

    if not photos:
        return

    # Create HTML snippet
    itag = u'<img style="width: 100%">'
    ebs = surllib.beautify(u'<h2></h2><p>%s</p>' %
                           u'<br/>'.join([itag] * len(photos)))
    ebs.h2.string = title
    for i, img in enumerate(ebs.select('img')):
        img['src'] = photos[i]

    msg = semail.Message(cname, 'pht', unicode(ebs))
    msg.setTitle(u'Billeder: %s' % title)
    msg.maybeSend()


def findPhotos(cname, bs):
    prefix = schildren.getChildURLPrefix(cname)

    for opt in bs.select('#sk-photos-toolbar-filter option'):
        if not opt.has_attr('value'):
            continue
        url = surllib.absurl(opt['value'])
        folder = opt.text.strip()
        if not url.startswith(prefix):
            config.clog(cname, u'Billeder: %s: ukendt URL %r' %
                        (folder, opt['value']))
            continue

        bs2 = surllib.skoleGetURL(url, True, MAX_CACHE_AGE)
        findPhotosInFolder(cname, bs2)


def skolePhotos(cname):
    url = schildren.getChildURL(cname, '/photos/archives')
    bs = surllib.skoleGetURL(url, True, MAX_CACHE_AGE)

    config.clog(cname, u'Kigger efter billeder')
    findPhotos(cname, bs)
