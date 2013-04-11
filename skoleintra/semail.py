#
# -*- encoding: utf-8 -*-
#
# email validator
# http://tools.ietf.org/tools/msglint/
#
import config
import md5
import re
import socket
import BeautifulSoup
import surllib
import time
import os
import glob
import codecs
import shutil
import smtplib
import mimetypes

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

def nicehtml(html):
    # ensure that the first <li is wrapped in a <ul
    oul = re.search('(?i)<[ou]l', html)
    li = re.search('(?i)<li', html)
    if li:
        if not oul or (li.start() < oul.start()):
            # add <ul>
            st = li.start()
            html = html[:st] + '</p><ul>' + html[st:]
    return BeautifulSoup.ICantBelieveItsBeautifulSoup(html).prettify().decode('utf-8')

def headerEncodeField(f):
    return str(Header(f, 'utf-8', 40))

def generateMIMEAttachment(path, data, usefilename=None):
    fn = usefilename if usefilename else os.path.basename(path)
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
    if type(fn) == unicode: fn = fn.encode('utf-8')
    msg.add_header('Content-Disposition', 'attachment', filename=('utf-8','',fn))

    return msg


class Message:
    def __init__(self, type, phtml):
        self.mp = {}

        self.mp['type']  = type # frontpage or ...
        self.mp['phtml'] = phtml # use self.data in general
        self.mp['data']  = str(phtml).decode('utf-8')
        self.mp['childname'] = config.CHILDNAME
        
        # not set by constructor
        self.mp['title'] = None
        self.mp['date']  = None
        self.mp['time']  = None
        self.mp['sender']  = None
        self.mp['recipient'] = None
        self.mp['mid'] = None
        self._email = None

    def __repr__(self):
        txt = u'<semail.Message'
        keys = 'type,mid,date,time,title,sender'.split(',')
        for key in keys:
            if key in self.mp and self.mp[key]:
                txt += u' %s=%s' % (key, repr(self.mp[key]))
        txt += u'>'
        return txt

    def setTitle(self, title, shorten = False):
        if shorten and len(title) > 40:
            title = title[:40] + title[40:].split(' ',2)[0] + '...'
        self.mp['title'] = title
    def setDate(self, date):
        date = date.strip()
        if ' ' in date: # also time
            date, time = date.split()
            self.setTime(time)
        self.mp['date'] = date
    def setTime(self, time):
        self.mp['time'] = time
    def setSender(self, sender):
        self.mp['sender'] = sender
    def setRecipient(self, recipient):
        self.mp['recipient'] = recipient
    def setMessageID(self, mid):
        self.mp['mid'] = mid

    def updatePersonDate(self, phtml = None):
        d = phtml.renderContents().decode('utf-8') if phtml else self.mp['data']
        assert(type(d) == unicode) # must be unicode

        # e.g. front page pics
        m = re.findall(u'>(?:Lagt ind|Skrevet) af ([^<]*?) den ([-0-9]*?)<', d)
        if m:
            m = m[-1]
            self.setSender(m[0])
            self.setDate(m[1])
            return
        
        m = re.findall(u'(?s)<small>Besked fra([^<]*?) - (?:modtaget|sendt) den ([^<]*?)</small>', d)
        if not m:
            m = re.findall(u'(?s)<small>Oprettet af([^<]*?) den ([^<]*?)</small>', d)

        if m:
            m = m[0]
            self.setSender(m[0].strip())
            self.setDate(m[1].strip())
            return
        else:
            # neither Sender nor date/time found
            config.log('No sender found', 2)
            return

    def prepareMessage(self):
        # add missing fields, if any

        if not self.mp.get('md5',None):
            keys = 'type,date,title,data'.split(',')
            txt = u' '.join([self.mp[x] for x in keys if self.mp.get(x, None)])
            self.mp['md5'] = unicode(md5.md5(txt.encode('utf-8')).hexdigest())

        if not self.mp.get('date', None):
            # use today as the date
            self.setDate(time.strftime('%d-%m-%Y')), # today

        # create nice version of the raw html
        if not 'nicehtml' in self.mp:
            self.mp['nicehtml'] = nicehtml(self.mp['data'])

    def getMessageID(self):
        if self.mp.get('mid', None):
            return self.mp['mid']
        else:
            self.prepareMessage()
            return self.mp['md5']

    def getLongMessageID(self):
        dt = '-'.join(reversed(self.mp['date'].split('-')))
        return '%s--%s' % (dt, self.getMessageID())

    def hasBeenSent(self):
        ''' Tests whether this email has previously been sent'''
        mid = self.getMessageID()
        old = glob.glob(os.path.join(config.MSG_DN, '*--%s'%mid))
        return old
                        
    def store(self):
        mid = self.getMessageID()
        dn = os.path.join(config.MSG_DN, self.getLongMessageID())
        if os.path.isdir(dn):
            # already stored - ignore!
            return False
        tdn = dn + '.tmp'
        if os.path.isdir(tdn):
            config.log('Removing previous temporary directory %s' % repr(tdn),2)
            shutil.rmtree(tdn) # Remove stuff
        os.mkdir(tdn)
        
        codecs.open(os.path.join(tdn, mid+'.eml'),'wb','utf-8').write(str(self.asEmail()))

        mpp = [(unicode(k), unicode(v)) for (k,v) in self.mp.items()]
        codecs.open(os.path.join(tdn, mid+'.txt'),'wb','utf-8').write(repr(mpp))
        
        os.rename(tdn, dn)        
        return True

    def asEmail(self):
        if self._email:
            return self._email
        self.prepareMessage()
        hostname = socket.getfqdn() # used below in a few places
        
        mpp = self.mp.copy()

        def wrapOrZap(key, title):
            val = self.mp.get(key,None)
            if val:
                mpp[key] = "<p class='%s' style='margin: 0;'>%s: %s</p>\n" % (key, title, val)
            else:
                mpp[key] = ''
                
        wrapOrZap('sender', 'Fra')
        wrapOrZap('recipient', 'Til')
        if mpp.get('time', None):
            mpp['ttime'] = u' '+mpp['time']
        else:
            mpp['ttime'] = u''

        # create initial HTML version
        html = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <title>%(title)s</title>
</head>
<body style='font-family: Verdana,Arial,Helvetica'>
<h1>%(title)s</h1>
<div class='meta' style='background-color: #eaeaea; color: #000; padding: 5px; margin: 0 0 10px 0;'>
%(sender)s%(recipient)s  <p class='date' style='margin: 0;'>Dato: %(date)s%(ttime)s</p>
</div>
<div class='text'>
  %(nicehtml)s
</div>
</body>
</html>
''' 
        html %= mpp
        html = BeautifulSoup.ICantBelieveItsBeautifulSoup(html)
        
        # first look for inline images (if any)
        # iimags: mapping from URL to (cid, binary string contents)
        iimgs = {}
        for imgtag in html.findAll('img'):
            url = imgtag['src']
            if url.lower().startswith('data:'):
                # ignore 'inline' images
                continue
            if url not in iimgs:
                data = surllib.skoleGetURL(url, False)
                cid = 'image%d-%f@%s' % (len(iimgs)+1, time.time(), hostname)
                iimgs[url] = (cid,data)
            cid, _ = iimgs[url]
            
            imgtag['src'] = 'cid:'+cid

        # next, handle attachments
        # attachments: email attachments ready for attachment :)
        attachments = []
        for atag in html.findAll('a'):
            try:
                url = atag['href']
            except KeyError:
                atag.replaceWithChildren() # kill the "broken" link
                continue
            url = atag['href']
            if 'Tilmelding/Oversigt.asp' in url:
                atag.replaceWithChildren() # kill link
                continue
            if url.startswith('/') or config.HOSTNAME in url: # onsite!
                data = None
                try:
                    data = surllib.skoleGetURL(url, False)
                except:
                    # unable to fetch URL
                    config.log(u'%s: Kan ikke hente flg. URL: %s' % (self.mp['title'] if self.mp['title'] else self, url))
                if data:
                    usefilename = atag['usefilename'] if atag.has_key('usefilename') else None
                    eatt = generateMIMEAttachment(url, data, usefilename)
                    attachments.append(eatt)
                    atag.replaceWithChildren() # kill the actual link


        # now, put the pieces together
        html = html.prettify().decode('utf-8')
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
                m.add_header('Content-ID', '<%s>'%cid)
                fn = os.path.basename(url).encode('utf-8')
                m.add_header('Content-Disposition', 'inline', filename=('utf-8','',fn))

                del m['MIME-Version']
                msg.attach(m)

            # attach attachments if any
            for attachment in attachments:
                del attachment['MIME-Version']
                msg.attach(attachment)
            
        # now for the general headers
        dt = self.mp['date']
        if self.mp.get('time',None): 
            dt += ' ' + self.mp['time']
        else:
            if dt == time.strftime('%d-%m-%Y'): # today
                ts = time.strftime('%H:%M:%S')
                if ts > '12:00:00':
                    ts = '12:00:00'
                dt += ' ' + ts
            else:
                dt += ' 12:00:00'
        dt = time.strptime(dt, '%d-%m-%Y %H:%M:%S')
        dt = email.utils.formatdate(time.mktime(dt),True)
        msg['Received'] = ('from %s ([127.0.0.1] helo=%s) '
                           'by %s with smtp (Skoleintra-Python) for %s; %s') % (hostname, hostname, hostname, config.EMAIL, dt)
        msg['Date'] = dt
                    
        title = self.mp['title']
        if self.mp['childname']:
            title = u'[%s] %s' % (self.mp['childname'], title)
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
            if self.mp.get(key,None):
                kkey = 'X-skoleintra-%s' % key
                msg[kkey] = Header(self.mp[key], 'utf-8', header_name=kkey)
        
        self._email = msg
        return msg

    def maybeSend(self):
        if self.hasBeenSent():
            config.log(u'Hopper tidligere sendt besked over: %s' % self, 2)
            return False
        self.send()
        
    def send(self):
        config.log(u'Sender email %s' % (self.mp['title'] if self.mp['title'] else self))
        msg = self.asEmail()
        # open smtp connection
        server = smtplib.SMTP('localhost')
        # server.set_debuglevel(1)
        server.sendmail(config.SENDER, config.EMAIL, msg.as_string())
        server.quit()
        
        # ensure that we only send once
        self.store()

_counter = 0
def maybeEmail(msg):
    global _counter
    msg.maybeSend()
