# -*- coding: utf-8 -*-

import bs4
import collections
import re
import time

import config
import schildren
import semail
import surllib

SECTION = 'frp'


def parseFrontpageItem(cname, div):

    # Do we have any comments?
    comments = div.find('div', 'sk-news-item-comments')
    cdiv = u''
    if comments:
        global c
        # Comments are enabled
        txt = comments.text.strip()
        m = re.match(ur'.*vis (\d+) kommentarer.*', txt.lower())
        assert(m)
        nc = int(m.group(1))
        if nc > 0:
            suff = '/news/pins/%s/comments' % div['data-feed-item-id']
            url = schildren.getChildURL(cname, suff)
            bs = surllib.skoleGetURL(url, asSoup=True, postData={'_': str(nc)})
            cdiv = unicode(bs.find('div', 'sk-comments-container'))
            cdiv = u'<br>' + cdiv

    author = div.find('div', 'sk-news-item-author')
    body = div.findAll('div', 'sk-user-input')[0]
    msg = semail.Message(cname, SECTION, unicode(body)+cdiv)

    title = body.get_text('\n').strip().split('\n')[0]
    title = ' '.join(title.replace(u'\xa0', ' ').strip().rstrip(' .').split())
    msg.setTitle(title, True)
    msg.setMessageID(div['data-feed-item-id'])
    msg.setSender(author.span.text)

    # Find list of recipients
    author.span.extract()  # Remove author
    for tag in [
            author.span,  # Remove author
            author.find('span', 'sk-news-item-for'),  # Remove 'til'
            author.find('span', 'sk-news-item-and'),  # Remove ' og '
            author.find('a', 'sk-news-show-more-link')]:
        if tag:
            tag.extract()
    recp = re.sub(ur'\s*(,| og )\s*', ',', author.text.strip())
    recp = recp.split(u',')
    msg.setRecipient(recp)

    msg.setDateTime(div.find('div', 'sk-news-item-timestamp').text)

    # Do we have any attachments?
    divA = div.find('div', 'sk-attachments-list')
    if divA:
        for att in (divA.findAll('a') or []):
            url = att['href']
            text = att.text.strip()
            msg.addAttachment(url, text)

    return msg


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
                    c.append(u" \U0001F1E9\U0001F1F0")  # Unicode DK Flag
                    c.append(surllib.todayComment())
                    msg = semail.Message(cname, SECTION, unicode(c))
                    msg.setTitle(c.text.strip())
                    msg.setDateTime(today)

                    msgs.append(msg)
                elif u'der er aktiviteter i dag' in uc:
                    continue  # ignore
                else:
                    config.clog(cname, u'Hopper mini-besked %r over' %
                                c.text.strip(), 2)

    # Find interesting main front page items
    fps = bs.findAll('div', 'sk-news-item')
    assert(len(fps) > 0)  # 1+ msgs on the frontpage or something is wrong
    for div in fps[::-1]:
        msg = parseFrontpageItem(cname, div)
        msgs.append(msg)

    return msgs


def getMsgsForChild(cname):
    url = schildren.getChildURL(cname, '/Index')
    config.clog(cname, u'Behandler forsiden %s' % url)
    bs = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    return parseFrontpage(cname, bs)


@config.Section(SECTION)
def skoleFrontpage(cnames):
    'Forside inkl. opslagstavle'
    msgs = collections.OrderedDict()
    for cname in cnames:
        for msg in getMsgsForChild(cname):
            if msg.hasBeenSent():
                continue
            config.clog(cname, u'Ny besked fundet: %s' % msg.mp['title'], 2)
            mid = msg.getLongMessageID()
            if mid in msgs:
                msgs[mid].addChild(cname)
            else:
                msgs[mid] = msg

    for mid, msg in msgs.items():
        cname = ','.join(msg.mp['children'])
        config.clog(cname, u'Sender ny besked: %s' % msg.mp['title'], 2)
        msg.maybeSend()
