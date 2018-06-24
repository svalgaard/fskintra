# -*- coding: utf-8 -*-

import config
import surllib
import semail
import re
import BeautifulSoup
import time
import schildren
import collections


def parseFrontpage(cname, bs):
    msgs = []

    # FIXME also look at birthdays

    # find interesting main front page items
    fps = bs.findAll('div', 'sk-news-item')
    assert(len(fps) > 2)  # at least two msgs on the frontpage or something is wrong
    for div in fps[::-1]:
        author = div.find('div', 'sk-news-item-author')
        body = div.findAll('div', 'sk-user-input')[0]
        msg = semail.Message(u'frontpage', body)
        msg.addChild(cname)

        msg.setTitle(body.text.strip(), True)
        # Do not use the msgid as we then may not notice updates
        # msg.setMessageID(div['data-feed-item-id'])
        msg.setSender(author.span.text)

        author.span.extract() # remove author
        author.span.extract() # remove 'til'
        for tag in [
            author.span, # remove author
            author.span, # remove 'til'
            author.find('span', 'sk-news-item-and'), # ' og '
            author.find('a', 'sk-news-show-more-link')]:
            if tag:
                tag.extract()
        msg.setRecipient(author.text)

        # 19. jun. 2018 => 19-06-2018
        dst = div.find('div', 'sk-news-item-timestamp').text
        ds = time.strptime(dst, '%d. %b. %Y')
        msg.setDate(time.strftime('%d-%m-%Y', ds))

        msgs.append(msg)

    return msgs


def getMsgsForChild(cname):
    url = schildren.getChildURLPrefix(cname) + '/Index'
    config.clog(cname, u'Behandler forsiden %s' % url)
    bs = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    return parseFrontpage(cname, bs)


def skoleFrontpage(cnames):
    msgs = collections.OrderedDict()
    for cname in cnames:
        for msg in getMsgsForChild(cname):
            if msg.hasBeenSent():
                continue
            config.clog(cname, u'Ny besked fundet: %s' % msg.mp['title'])
            mid = msg.getLongMessageID()
            if mid in msgs:
                msgs[mid].addChild(cname)
            else:
                msgs[mid] = msg

    for msg in msgs:
        cname = ','.join(msgs.mp['children'])
        config.clog(cname, u'Ny besked fundet: %s' % msg.mp['title'])
        msg.maybeSend()
