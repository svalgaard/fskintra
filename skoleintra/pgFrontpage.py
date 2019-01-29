# -*- coding: utf-8 -*-

import collections
import re
import time

import config
import sbs4
import schildren
import semail
import surllib

SECTION = 'frp'


def parseFrontpageItem(cname, div):
    '''Parse a single frontpage news item'''
    # Do we have any comments?
    comments = div.find('div', 'sk-news-item-comments')
    cdiv = u''
    if comments:
        global c
        # Comments are enabled
        txt = comments.text.strip()
        if u'tilføj' not in txt.lower():
            m = re.match(ur'.*vis (\d+) kommentar.*', txt.lower())
            assert(m)
            nc = int(m.group(1))
            if nc > 0:
                suff = '/news/pins/%s/comments' % div['data-feed-item-id']
                url = schildren.getChildURL(cname, suff)
                bs = surllib.skoleGetURL(url, asSoup=True, postData={'_': str(nc)})
                cdiv = unicode(bs.find('div', 'sk-comments-container'))
                cdiv = u'<br>' + cdiv

    author = div.find('div', 'sk-news-item-author')
    body = div.find('div', 'sk-news-item-content')
    # trim the body a bit
    body = sbs4.copy(body)  # make a copy as we look for attachments later
    for e in body.select('.sk-news-item-footer, .sk-news-item-comments'):
        e.extract()
    for e in body.select('.h-fnt-bd'):
        e['style'] = 'font-weight: bold'
    for e in body.select('div'):
        # remove empty divs
        contents = u''.join(map(unicode, e.children)).strip()
        if not contents:
            e.extract()
    # Trim extra white space - sometimes unecessary linebreaks are introduced
    sbs4.trimSoup(body)

    msg = semail.Message(cname, SECTION, unicode(body)+cdiv)

    for e in body.select('span, strong, b, i'):
        e.unwrap()
    sbs4.condenseSoup(body)

    title = body.get_text(u'\n', strip=True).strip().split(u'\n')[0]
    title = title.replace(u'\xa0', u' ').strip()
    title = u' '.join(title.rstrip(u' .').split())

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
    '''Look for new frontpage news items'''
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
                    sbs4.appendTodayComment(c)
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
    '''Look for new frontpage news'''
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
