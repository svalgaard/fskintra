# -*- coding: utf-8 -*-

#
# email validator
# http://tools.ietf.org/tools/msglint/
#

import codecs
import glob
import imghdr
import md5
import mimetypes
import os
import shutil
import smtplib
import socket
import urllib
import urllib2
import time

import config
import surllib

import email
from email import encoders
from email.header import Header
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# set quoted-printable as default (instead of base64)
email.Charset.add_charset('utf-8', email.Charset.QP, email.Charset.QP, 'utf-8')


def headerEncodeField(f):
    try:
        f.encode('ascii')
        return str(Header(f, 'ascii', 40))
    except UnicodeEncodeError:
        return str(Header(f, 'utf-8', 40))


def generateMIMEAttachment(path, data, usefilename=None):
    fn = usefilename if usefilename else os.path.basename(path)
    fn = urllib.unquote(fn)
    ctype, encoding = mimetypes.guess_type(fn)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        # Note: we should handle calculating the charset
        msg = MIMEText(data, _subtype=subtype)
    elif maintype == 'image':
        msg = MIMEImage(data, _subtype=subtype)
    elif maintype == 'audio':
        msg = MIMEAudio(data, _subtype=subtype)
    else:
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(data)
        encoders.encode_base64(msg)
    # Encode the payload using Base64
    # do not do this here - already done above.
    # encoders.encode_base64(msg)
    # Set the filename parameter
    if type(fn) != unicode:
        fn = fn.decode('utf-8')
    fne = headerEncodeField(fn)
    msg.add_header('Content-Disposition', 'attachment', filename=fne)
    msg.set_param('name', fne)
    return msg


class Message:
    def __init__(self, cname, tp, html):
        self.mp = {}

        assert(type(cname) == unicode and cname)
        self.mp['children'] = [cname]
        assert(type(tp) == str and len(tp) == 3)
        self.mp['type'] = tp  # msg or ...
        assert(type(html) == unicode)
        self.mp['html'] = html  # html content

        self.mp['title'] = None
        self.mp['sender'] = None
        self.mp['recipient'] = None
        self.mp['cc'] = None
        # use today by default
        self.mp['date_ts'] = time.localtime()
        self.mp['date'] = time.strftime('%Y-%m-%d', self.mp['date_ts'])
        self.mp['date_string'] = self.mp['date']
        self.mp['date-set'] = False
        self.mp['mid'] = None
        self.mp['attatchments'] = []
        self.mp['md5'] = ''
        self._email = None

    def __repr__(self):
        txt = u'<semail.Message'
        keys = 'type,mid,date,title,sender'.split(',')
        for key in keys:
            if self.mp.get(key):
                txt += u' %s=%s' % (key, repr(self.mp[key]))
        txt += u'>'
        return txt

    def setTitle(self, title, shorten=False):
        assert(type(title) == unicode)
        if shorten and len(title) > 40:
            title = title[:40] + title[40:].split(' ', 2)[0] + '...'
        self.mp['title'] = title

    def addChild(self, cname):
        assert(type(cname) == unicode and cname)
        if cname not in self.mp['children']:
            self.mp['children'].append(cname)

    def setDateTime(self, dt):
        assert(type(dt) == unicode)
        ts = time.localtime()  # use "NOW" by default

        dt2 = dt.split(',')[-1].strip().replace('.', '')
        if ':' not in dt2:
            dt2 += ' 12:00'
        try:
            # 25. jun. 2018 16:26
            ts = time.strptime(dt2, '%d %b %Y %H:%M')
        except ValueError:
            config.log(u'Ukendt tidsstempel %r' % dt, -1)
            assert(False)  # FIXME We should never be here

        self.mp['date_string'] = dt
        self.mp['date_ts'] = ts
        self.mp['date'] = time.strftime('%Y-%m-%d', ts)
        self.mp['date-set'] = True

    def setSender(self, sender):
        assert(type(sender) == unicode)
        self.mp['sender'] = sender

    def setRecipient(self, recipient):
        if type(recipient) == list and recipient:
            N = 9
            if len(recipient) == 1:
                recipient = recipient[0]
            else:
                if len(recipient) > N + 1:
                    last = u'%d andre' % (len(recipient)-N)
                    recipient = recipient[:N] + [last]
                recipient = u', '.join(recipient[:-1]) + ' og ' + recipient[-1]

        assert(type(recipient) == unicode)
        self.mp['recipient'] = recipient

    def setCC(self, cc):
        assert(type(cc) == unicode)
        self.mp['cc'] = cc

    def setMessageID(self, *mid):
        assert(mid)
        self.mp['mid'] = '--'.join(str(m) for m in mid)
        assert(type(self.mp['mid']) == str)  # mid must be ascii

    def addAttachment(self, url, text):
        assert(type(url) in [str, unicode])
        assert(type(text) == unicode)
        self.mp['attatchments'].append((surllib.absurl(url), text))

    def prepareMessage(self):
        # add missing fields, if any
        if not self.mp.get('md5', None):
            keys = 'type,date,title,html'.split(',')
            if not self.mp['date-set']:
                keys.remove('date')
            txt = u' '.join([self.mp[x] for x in keys if self.mp.get(x, None)])
            self.mp['md5'] = md5.md5(txt.encode('utf-8')).hexdigest()

    def getMessageID(self):
        '''Format: type--md5(--mid), e.g.,
frp--625922d86ffef60cfef5efc7822a7cff
msg--625922d86ffef60cfef5efc7822a7cff--123456'''

        # ensure that md5 has been calculated
        self.prepareMessage()

        m = '%(type)s--%(md5)s' % self.mp
        if self.mp.get('mid', None):
            m += '--%(mid)s' % self.mp
        assert(type(m) == str)
        assert('/' not in m)

        return m

    def getLongMessageID(self):
        '''Format: 'date--' + short MessageID'''

        return '%s--%s' % (self.mp['date'], self.getMessageID())

    def hasBeenSent(self):
        ''' Tests whether this email has previously been sent'''
        self.prepareMessage()

        # Check only type and md5
        return hasSentMessage(tp=self.mp['type'], md5=self.mp['md5'])

    def store(self):
        mid = self.getMessageID()
        dn = os.path.join(config.MSG_DN, self.getLongMessageID())
        if os.path.isdir(dn):
            # already stored - ignore!
            return False
        tdn = dn + '.tmp'
        if os.path.isdir(tdn):
            config.log('Removing previous temporary directory %s' %
                       repr(tdn), 2)
            shutil.rmtree(tdn)  # Remove stuff
        os.mkdir(tdn)

        fd = open(os.path.join(tdn, mid + '.eml'), 'wb')
        fd.write(str(self.asEmail()))
        fd.close()

        mpp = [(unicode(k), unicode(v)) for (k, v) in self.mp.items()]
        fd = codecs.open(os.path.join(tdn, mid + '.txt'), 'wb', 'utf-8')
        fd.write(repr(mpp))
        fd.close()

        os.rename(tdn, dn)
        return True

    def asEmail(self):
        if self._email:
            return self._email
        self.prepareMessage()
        hostname = socket.getfqdn()  # used below in a few places

        mpp = self.mp.copy()

        def wrapOrZap(key, title, tag=''):
            if title:
                title += u': '
            val = mpp.get(key, None)
            if val:
                if tag:
                    val = u'<%s>%s</%s>' % (tag, val, tag.split()[0])
                mpp[key] = (u"<span style='font-size: 15px'>"
                            u"%s%s</span><br>\n  ") % (title, val)
            else:
                mpp[key] = ''

        wrapOrZap('sender', '', 'b style="font-size: 17px"')
        wrapOrZap('recipient', 'Til')
        wrapOrZap('cc', 'Kopi til')

        # create initial HTML version
        html = u'''<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <title>%(title)s</title>
</head>
<body style='font-family: Helvetica, sans-serif; font-size: 14px;'>
<h1>%(title)s</h1>
<div class='header' style='padding: 5px; background-color: #eee; margin-bottom: 15px;'>
  %(sender)s%(recipient)s%(cc)s<span>%(date_string)s</span>
</div>
<div class='text'>
  %(html)s
</div>
</body>
</html>''' % mpp
        html = surllib.beautify(html)

        # first look for inline images (if any)
        # iimags: mapping from URL to (cid, binary string contents)
        iimgs = {}
        for imgtag in html.findAll('img'):
            if not imgtag.has_attr('src'):
                continue  # ignore
            url = imgtag['src']
            if url.lower().startswith('data:'):
                # ignore 'inline' images
                continue
            elif not url:
                # ignore empty URLs
                continue
            if url not in iimgs:
                try:
                    data = surllib.skoleGetURL(url, False)
                except urllib2.URLError:
                    # could not fetch URL for some reason - ignore
                    continue
                # is this actually an image?
                if not imghdr.what('', data):
                    continue  # ignore
                cid = 'image%d-%f@%s' % (len(iimgs) + 1, time.time(), hostname)
                iimgs[url] = (cid, data)
            cid, _ = iimgs[url]

            imgtag['src'] = 'cid:' + cid

        # next, handle attachments
        # attachments: email attachments ready for attachment :)
        attachments = []
        for atag in html.findAll('a'):
            try:
                url = atag['href']
            except KeyError:
                atag.replaceWithChildren()  # kill the "broken" link
                continue
            url = atag['href']
            if url.startswith('/') or config.HOSTNAME in url:  # onsite!
                data = None
                try:
                    data = surllib.skoleGetURL(url, False)
                except:
                    # unable to fetch URL
                    config.log(u'%s: Kan ikke hente flg. URL: %s' %
                               (self.mp['title'] if self.mp['title'] else self,
                                url))
                if data:
                    eatt = generateMIMEAttachment(url, data, None)
                    attachments.append(eatt)
                    atag.replaceWithChildren()  # kill the actual link

        # Attach actual attachments (if any)
        for (url, text) in self.mp['attatchments']:
            data = surllib.skoleGetURL(url, False)
            eatt = generateMIMEAttachment(url, data, text)
            attachments.append(eatt)

        # now, put the pieces together
        html = html.prettify()
        msgHtml = MIMEText(html, 'html', 'utf-8')
        if not iimgs and not attachments:
            # pure HTML version
            msg = msgHtml
        else:
            # inline images but no attachments
            #   multipart/related
            #     text/html with html text
            #     image/xxx with inline images
            # OR
            # email with inline images + attachment
            #   multipart/mixed
            #     text/html med html udgave
            #     image/gif med billede
            #     application/xxx with word document
            if attachments:
                msg = MIMEMultipart('mixed', type='text/html')
            else:
                msg = MIMEMultipart('related', type='text/html')
            del msgHtml['MIME-Version']
            msg.attach(msgHtml)

            # attach images if any
            for (url, (cid, data)) in iimgs.items():
                m = MIMEImage(data)
                m.add_header('Content-ID', '<%s>' % cid)
                fn = os.path.basename(url).encode('utf-8')
                m.add_header('Content-Disposition', 'inline',
                             filename=('utf-8', '', fn))

                del m['MIME-Version']
                msg.attach(m)

            # attach attachments if any
            for attachment in attachments:
                del attachment['MIME-Version']
                msg.attach(attachment)

        # now for the general headers
        dt = email.utils.formatdate(time.mktime(self.mp['date_ts']), True)
        msg['Received'] = ('from %s ([127.0.0.1] helo=%s) '
                           'by %s with smtp (fskintra) for %s; %s'
                           ) % (hostname, hostname, hostname, config.EMAIL, dt)
        msg['Date'] = dt

        title = self.mp['title']
        if self.mp['children']:
            title = u'[%s] %s' % (', '.join(self.mp['children']), title)
        msg['Subject'] = Header(title, 'utf-8', 60)
        if 'sender' in self.mp and self.mp['sender']:
            sender = u'Skoleintra - %s' % self.mp['sender']
        else:
            sender = u'Skoleintra'
        sender = headerEncodeField(sender) + u' <%s>' % config.SENDER
        msg['From'] = sender
        msg['To'] = config.EMAIL

        # other tags just for ourselves
        keys = 'mid,md5'.split(',')
        for key in keys:
            if self.mp.get(key, None):
                kkey = 'X-skoleintra-%s' % key
                msg[kkey] = Header(self.mp[key], 'utf-8', header_name=kkey)

        self._email = msg
        return msg

    def maybeSend(self):
        if self.hasBeenSent():
            config.log(u'Hopper tidligere sendt besked over: %s' % self, 2)
            return False
        self.send()
        return True

    def send(self):
        config.log(u'Sender email %s' %
                   (self.mp['title'] if self.mp['title'] else self))
        if config.CATCHUP:
            config.log(u'(sendes faktisk ikke pga --catchup)')
            return self.store()

        msg = self.asEmail()
        # open smtp connection
        if config.SMTPHOST:
            server = smtplib.SMTP(config.SMTPHOST, config.SMTPPORT)
        else:
            server = smtplib.SMTP('localhost')
        # server.set_debuglevel(1)
        if config.SMTPLOGIN:
            try:
                server.starttls()
            except smtplib.SMTPException:
                pass  # ok, but we tried...
            server.login(config.SMTPLOGIN, config.SMTPPASS)
        server.sendmail(config.SENDER, config.EMAIL, msg.as_string())
        server.quit()

        # ensure that we only send once
        self.store()


def hasSentMessage(date='', tp='', md5='', mid=''):

    if not date:
        date = '?' * 10
    if not tp:
        tp = '?' * 3
    if not md5:
        md5 = '?' * 32
    if type(mid) in [list, tuple]:
        mid = str('--'.join(mid))

    spath = '--'.join((date, tp, md5))

    if mid:
        spath += '--' + mid
    else:
        spath += '*'

    path = os.path.join(config.MSG_DN, spath)

    assert(type(path) == str)
    assert('/' not in spath)

    return bool(glob.glob(path))
