# -*- coding: utf-8 -*-

import re
import config
import surllib
import semail
import sys
import json
import collections
import schildren
import time


def msgFromJson(cname, threadId, msg):
    '''Input is a decoded JSON representation of a message (Besked).
Output is an semail.Message ready to be sent'''

    # We have never seen this set to anything -- need to check
    # when this happens
    assert(not msg['AdditionalLinkUrl'])

    html = u'<div class="base">%s</div>\n' % msg['BaseText']
    if msg['PreviousMessagesText']:
        html += u'<div class="prev">%s</div>\n' % msg['PreviousMessagesText']

    emsg = semail.Message(u'message', html)
    emsg.addChild(cname)
    emsg.setMessageID(threadId, unicode(msg["Id"]))
    emsg.setTitle(msg['Subject'])
    emsg.setDateTime(msg['SentReceivedDateText'])
    emsg.setRecipient(msg['Recipients'])
    emsg.setSender(msg['SenderName'])
    for att in (msg['AttachmentsLinks'] or []):
        emsg.addAttachment(att['HrefAttributeValue'], att['Text'])
    return emsg


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
            config.clog(cname, 'Noget galt i tråd %d %r %r' % (i, tid, lmid), -1)
            continue

        if semail.hasSeenMessage(tid, lmid):
            continue

        # This last messages has not been seen - load the entire conversation
        suffix = (
            '/messages/conversations/loadmessagesforselectedconversation' +
            '?threadId=' + tid +
            '&takeFromRootMessageId=' + lmid +
            '&takeToMessageId=0' +
            '&searchRequest=' +
            '&_=' + str(int(time.time()*1000)))
        curl = schildren.getChildURL(cname, suffix)
        data = surllib.skoleGetURL(curl, asSoup=False, noCache=True)

        try:
            msgs = json.loads(data)
        except ValueError:
            config.clog(cname, 'Kan ikke indlæse besked-listen i tråd %d %r %r' % (i, tid, lmid), -1)
            continue

        assert(type(msgs) == list)
        for msg in msgs[::-1]:
            mid = unicode(msg.get('Id'))
            if semail.hasSeenMessage(tid, mid):
                continue

            # Generate new messages with this content
            emsgs.append(msgFromJson(cname, tid, msg))

    return emsgs


def getMsgsForChild(cname):
    url = schildren.getChildURL(cname, '/messages/conversations')
    config.clog(cname, u'Kigger efter nye beskeder på %s' % url)
    bs = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    return parseMessages(cname, bs)


def skoleDialogue(cnames):
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
