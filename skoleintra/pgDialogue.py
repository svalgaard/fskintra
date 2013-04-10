#
# -*- encoding: utf-8 -*-
#

import re
import config
import surllib
import semail
import mechanize

URL_PREFIX     = '/Infoweb/Fi/Besked/'
URL_BOX_PREFIX = URL_PREFIX + 'Oversigt.asp?Bakke='
TRAYS = ('ind', 'ud')

def diaExamineMessage(url, mid):
    bs = surllib.skoleGetURL(url, True)
    
    # first, find main text
    tr = bs.find('tr', valign='top')
    assert(tr)
    phtml = tr.find('td')
    msg = semail.Message(u'dialogue', phtml)
    msg.setMessageID(mid)
    
    # next, look at the header
    header = bs.find('table', 'linje1')
    assert(header) # there must be a header
    headerLines = header.findAll('tr')
    assert(len(headerLines) >= 3) # there must be something inside the header

    for hl in headerLines:
        txt = hl.text
        if not txt:
            continue # ignore 
        elif txt.startswith(u'Denne besked slettes'):
            pass # ignore
        elif hl.find('h4'):
            # title
            msg.setTitle(txt)
        elif txt.startswith(u'Besked fra') or txt.startswith(u'Oprettet af'):
            # Besked fra Frk Nielsen - modtaget den 26-09-2012 20:29:44	
            msg.updatePersonDate(hl)
        elif txt.startswith(u'Sendt til '):
            # Sendt til ... 
            msg.setRecipient(txt.split(u' ', 2)[-1])
        else:
            config.log(u'Ukendt header i besked #%s: %s' % (mid, txt),-1)
            
    msg.maybeSend()
    
def diaFindMessages(data):
    global URL_PREFIX
    bs = surllib.beautify(data)

    atags = bs.findAll('a')
    for atag in atags:
        href = atag['href']
        
        if not href.startswith('VisBesked'):
            continue # ignore

        title = atag.text.strip()
        if not title:
            continue # ignore (this is the envelope icon)

        lurl = 'https://%s%s%s' % (config.HOSTNAME, URL_PREFIX, href)
        mid = re.search('Id=(\\d+)', href).group(1)

        diaExamineMessage(lurl, mid)

def skoleDialogue():
    global URL_BOX_PREFIX, TRAYS
    surllib.skoleLogin()
    br = surllib.getBrowser()

    for tray in TRAYS:
        config.log(u'Behandler beskeder i bakken %s' % tray)

        url = 'https://%s%s%s' % (config.HOSTNAME, URL_BOX_PREFIX, tray)
        
        # first read the initial page
        resp = br.open(url)
        data = resp.read()
        diaFindMessages(data)
        
        # select specific class
        try:
            br.select_form(name='FrontPage_Form1')
        except mechanize._mechanize.FormNotFoundError, e:
            # ignore
            continue
        br['R1'] = ('klasse',)
        
        resp = br.submit()
        data = resp.read()
        diaFindMessages(data)

if __name__ == '__main__':
    # test
    skoleDialogue()
