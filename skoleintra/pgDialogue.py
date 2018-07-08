# -*- coding: utf-8 -*-

import collections
import json
import re
import sys

import config
import schildren
import semail
import surllib


def find1orFail(bs, selector, asText=False):
    hits = bs.select(selector)
    if len(hits) != 1:
        config.log(u"'%s' var %d gange på siden (!=1)" % (selector, len(hits)))
        sys.exit(1)
    hit = hits[0]
    if asText:
        hit = hit.text.strip()
    return hit


def filteredContents(bs):
    return u''.join(unicode(c) for c in bs.contents).strip()


def msgFromJson(cname, jsn, threadId=''):
    '''Input is a decoded JSON representation of a message (Besked).
Output is an semail.Message ready to be sent'''

    # We have never seen this set to anything -- need to check
    # when this happens
    assert(not jsn['AdditionalLinkUrl'])

    html = u'<div class="base">%s</div>\n' % jsn['BaseText']
    if jsn['PreviousMessagesText']:
        html += u'<div class="prev">%s</div>\n' % jsn['PreviousMessagesText']

    msg = semail.Message(cname, 'msg', html)
    if threadId:
        msg.setMessageID(threadId, str(jsn["Id"]))
    else:
        msg.setMessageID(str(jsn["Id"]))
    msg.setTitle(jsn['Subject'])
    msg.setDateTime(jsn['SentReceivedDateText'])
    msg.setRecipient(jsn['Recipients'])
    msg.setSender(jsn['SenderName'])
    for att in (jsn['AttachmentsLinks'] or []):
        msg.addAttachment(att['HrefAttributeValue'], att['Text'])
    return msg


def parseTrayMessage(cname, bs, mid, sender):
    jsn = {}
    jsn['Id'] = int(mid)
    jsn['SenderName'] = sender
    jsn['AdditionalLinkUrl'] = ''
    jsn['Subject'] = find1orFail(bs, 'div.sk-message-subject-text', True)
    jsn['SentReceivedDateText'] = find1orFail(
        bs, 'div.sk-message-send-date', True)
    jsn['BaseText'] = filteredContents(find1orFail(bs, 'div.sk-message-text'))

    # Maybe we also have "Reply/Forward text"
    div = bs.select('div.sk-message-text + a + div')
    jsn['PreviousMessagesText'] = filteredContents(div[0]) if div else u''

    # Do we have any attachments?
    jsn['AttachmentsLinks'] = []
    for a in bs.select('div.sk-attachments-list a'):
        jsn['AttachmentsLinks'].append({
            'HrefAttributeValue': a['href'],
            'Text': a.text.strip()
        })

    # Find list of recipients
    s = 'div.sk-message-senderrecipient-name'
    if bs.select('.sk-message-title-rows-container ' + s):
        rec = find1orFail(bs, '.sk-message-title-rows-container ' + s)
    else:
        rec = find1orFail(bs, s)
    rec.span.extract()  # remove 'Til:'
    more = rec.find('a', 'sk-message-show-more-link')
    if more:
        more.extract()  # remove Vis ... mere
    jsn['Recipients'] = re.split(ur'\s*(?:,| og )\s*', rec.text.strip())

    return msgFromJson(cname, jsn)


def parseTrayMessages(cname, bs):
    msgs = []

    for div in bs.select('.sk-message-list-item'):
        url = div.find('a')['href']

        mid = re.findall('(?<=/message/)[0-9]+', url)
        assert(len(mid) == 1 and mid[0])
        mid = mid[0]

        sender = div.find('li', 'sk-message-senderrecipient-name').text.strip()
        m = re.match(r'^([^(]*) \(.*\)$', sender)
        if m:
            sender = m.group(1)

        # We could also get the title
        title = div.find('div', 'sk-message-title').text.strip()

        if semail.hasSentMessage(tp='msg', mid=mid):
            continue

        config.clog(cname, u'Henter ny besked: %s - %s' % (sender, title), 2)
        bs = surllib.skoleGetURL(url, True)

        msg = parseTrayMessage(cname, bs, mid, sender)
        msgs.append(msg)

    return msgs


def parseMessages(cname, bs):
    # Look for a div with a very long attribute with json
    main = bs.find('div', 'sk-l-content-wrapper')
    conversations = None
    for d in main.findAll('div'):
        for a in d.attrs:
            if 'message' not in a.lower() or len(d[a]) < 100:
                continue
            try:
                jsn = json.loads(d[a])
                if type(jsn) == dict:
                    conversations = jsn.get('Conversations')
                    break
            except ValueError:
                continue

    if not conversations:
        config.clog(cname, 'Ingen beskeder fundet?!?', -1)
        return []

    emsgs = []
    for i, c in enumerate(conversations[::1]):
        tid = c.get('ThreadId')
        lmid = unicode(c.get('LatestMessageId'))
        if not tid or not lmid:
            config.clog(cname, 'Noget galt i tråd %d %r %r'
                        % (i, tid, lmid), -1)
            continue

        if semail.hasSentMessage(tp='msg', mid=(tid, lmid)):
            continue

        # This last messages has not been seen - load the entire conversation
        suffix = (
            '/messages/conversations/loadmessagesforselectedconversation' +
            '?threadId=' + tid +
            '&takeFromRootMessageId=' + lmid +
            '&takeToMessageId=0' +
            '&searchRequest=')
        curl = schildren.getChildURL(cname, suffix)
        data = surllib.skoleGetURL(curl, asSoup=False, noCache=True,
                                   addTimeSuffix=True)

        try:
            msgs = json.loads(data)
        except ValueError:
            config.clog(cname, 'Kan ikke indlæse besked-listen i tråd %d %r %r'
                        % (i, tid, lmid), -1)
            continue

        assert(type(msgs) == list)
        for jsn in msgs[::-1]:
            mid = unicode(jsn.get('Id'))
            if semail.hasSentMessage(tp='msg', mid=(tid, mid)):
                continue

            # Generate new messages with this content
            emsgs.append(msgFromJson(cname, jsn, tid))

    return emsgs


def getMsgsForChild(cname):
    dtype = surllib.getBrowser().getState('dialogue')
    if dtype == 'conversations':
        url = schildren.getChildURL(cname, '/messages/conversations')
        config.clog(cname, u'Kigger efter nye beskeder på %s' % url)
        bs = surllib.skoleGetURL(url, asSoup=True, noCache=True)

        return parseMessages(cname, bs)
    elif dtype == 'inbox':
        msgs = []
        for tray in ['inbox', 'outbox']:
            url = schildren.getChildURL(cname, '/messages/'+tray)
            config.clog(cname, u'Kigger efter nye beskeder på %s' % url)
            bs = surllib.skoleGetURL(url, asSoup=True, noCache=True)

            msgs += parseTrayMessages(cname, bs)

        return msgs
    else:
        config.clog(cname, u'Beskede-indbakke-type %r ikke understøttet'
                    % dtype, 0)
        return []


def skoleDialogue(cnames):
    msgs = collections.OrderedDict()
    for cname in cnames[:1]:
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
