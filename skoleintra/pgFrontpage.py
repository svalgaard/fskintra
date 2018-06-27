# -*- coding: utf-8 -*-

import config
import surllib
import semail
import re
import bs4
import time
import schildren
import collections


def parseFrontpage(cname, bs):
    msgs = []

    # Find potential interesting events today in the sidebar
    ul = bs.find('ul', 'sk-reminders-container')
    if ul:
        for li in ul.findAll('li', recursive=False):
            for c in li.contents:
                uc = unicode(c).strip().lower()
                if not uc:
                    continue
                if u'har fødselsdag' in uc:
                    today = unicode(time.strftime(u'%d. %b. %Y'))
                    c.insert(0, u"\U0001F1E9\U0001F1F0 ")  # Unicode Danish Flag
                    text = c.text.strip()
                    c.append(bs4.Comment(' I dag er %s ' % today))
                    msg = semail.Message(u'frontpage', unicode(c))
                    msg.addChild(cname)
                    msg.setTitle(c.text.strip())
                    msg.setDateTime(today)

                    msgs.append(msg)
                elif u'der er aktiviteter i dag' in uc:
                    continue  # ignore
                else:
                    config.clog(cname, u'Hopper mini-besked %r over' % c.text.strip())

    # find interesting main front page items
    fps = bs.findAll('div', 'sk-news-item')
    assert(len(fps) > 2)  # at least two msgs on the frontpage or something is wrong
    for div in fps[::-1]:
        author = div.find('div', 'sk-news-item-author')
        body = div.findAll('div', 'sk-user-input')[0]
        msg = semail.Message(u'frontpage', unicode(body))
        msg.addChild(cname)

        msg.setTitle(body.get_text('\n').strip().split('\n')[0].strip(), True)
        # Do not use the msgid as we then may not notice updates
        # msg.setMessageID(div['data-feed-item-id'])
        msg.setSender(author.span.text)

        # find list of reciepients
        author.span.extract() # remove author
        for tag in [
            author.span, # remove author
            author.find('span', 'sk-news-item-for'), # remove 'til'
            author.find('span', 'sk-news-item-and'), # ' og '
            author.find('a', 'sk-news-show-more-link')]:
            if tag:
                tag.extract()
        recp = re.sub(ur'\s*(,| og )\s*', ',', author.text.strip())
        recp = recp.split(u',')
        msg.setRecipient(recp)

        msg.setDateTime(div.find('div', 'sk-news-item-timestamp').text)

        # do we have any attachments?
        divA = div.find('div', 'sk-attachments-list')
        if divA:
            for att in (divA.findAll('a') or []):
                url = att['href']
                text = att.text.strip()
                msg.addAttachment(url, text)

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

    for mid, msg in msgs.items():
        cname = ','.join(msg.mp['children'])
        config.clog(cname, u'Ny besked fundet: %s' % msg.mp['title'])
        msg.maybeSend()
