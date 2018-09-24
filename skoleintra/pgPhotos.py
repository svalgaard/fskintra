# -*- coding: utf-8 -*-

import glob
import json
import md5
import os

import config
import sbs4
import schildren
import semail
import surllib

SECTION = 'pht'
MAX_CACHE_AGE = .99
PHOTOS_PER_EMAIL = 50


def sendPhotos(cname, title, mid, photos):

    # First determine if any of the photos were sent earlier
    previouslySent = set()
    for dn in semail.hasSentMessage(tp=SECTION, mid=mid):
        for fn in glob.glob(os.path.join(dn, '*.json')):
            try:
                jsn = json.load(open(fn))
            except ValueError:
                continue  # Simply ignore files with wrong JSON
            data = jsn.get('data')
            if data:
                previouslySent.update(data)

    pending = list(url for url in photos if url not in previouslySent)

    if not pending:
        return

    if len(photos) - len(pending) < 5:
        # At most 5 pictures has been sent earlier - send them all again
        pending = photos

    # Send the photos in e-mails of PHOTOS_PER_EMAIL pictures
    ecount = (len(pending)-1) / PHOTOS_PER_EMAIL + 1

    for ei in range(ecount):
        pics = pending[:PHOTOS_PER_EMAIL]
        del pending[:PHOTOS_PER_EMAIL]

        # Create HTML snippet
        itag = u'<img style="max-width: 100%">'
        ebs = sbs4.beautify(u'<h2></h2><p>%s</p>' %
                            u'<br/>'.join([itag] * len(pics)))
        ebs.h2.string = title
        for i, img in enumerate(ebs.select('img')):
            img['src'] = pics[i]

        msg = semail.Message(cname, SECTION, unicode(ebs))
        if ecount > 1:
            msg.setTitle(u'Billeder: %s (%d/%d)' % (title, ei+1, ecount))
        else:
            msg.setTitle(u'Billeder: %s' % title)
        msg.setMessageID(mid)
        msg.setData(pics)
        msg.maybeSend()


def findPhotosInFolder(cname, url, bs):
    title = bs.h2.text.strip()
    mid = md5.md5(url.encode('utf-8')).hexdigest()[::2]
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

    sendPhotos(cname, title, mid, photos)


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
        findPhotosInFolder(cname, url, bs2)


@config.Section(SECTION)
def skolePhotos(cname):
    'Billeder'
    url = schildren.getChildURL(cname, '/photos/archives')
    bs = surllib.skoleGetURL(url, True, MAX_CACHE_AGE)

    config.clog(cname, u'Kigger efter billeder')
    findPhotos(cname, bs)
