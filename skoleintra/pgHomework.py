# -*- coding: utf-8 -*-

import config
import glob
import os
import json
import schildren
import semail
import surllib
import md5
import re
from datetime import datetime

SECTION = 'hwk'


def formatHomework(cname, bs):
    '''Format the homework nicely for email'''
    # Test if there is any homework
    if not bs.select('div.sk-white-box > b'):
        return '', ''
    html = u''
    homework_checksums = set()
    # First determine if some of the homework were sent earlier
    previouslySent = set()
    for dn in semail.hasSentMessage(tp=SECTION):
        for fn in glob.glob(os.path.join(dn, '*.json')):
            try:
                jsn = json.load(open(fn))
            except ValueError:
                continue  # Simply ignore files with wrong JSON
            data = jsn.get('data')
            if data:
                previouslySent.update(data)
    # print(previouslySent)

    for li in bs.select('ul.sk-list > li'):
        # Locate header with due-dates
        header = li.find('div', 'sk-white-box').b.text
        config.clog(cname, u'Fandt lektietitel: %r' % header, 3)
        if type(header) == str:
            header = header.decode('utf-8')
        html_temp = u'<b>{0}</b>'.format(header)
        html_temp += u'<table border="1" cellpadding="1" cellspacing="1">'
        html_temp += u'<tbody>'
        # Locate each table with homework
        table = li.find('table')
        for row in table.select('tbody tr'):
            delete_row = False
            # Loop through each cell in the row
            for cell in row.find_all('td'):
                # Remove unneded tags
                if cell.find('span'):
                    cell.span.unwrap()
                if cell.find('div'):
                    for div in cell.find_all('div'):
                        cell.div.unwrap()
                del cell['style']
                cell.string = '<br/>'.join(cell.stripped_strings)
                if cell.string == '':  # '\xa0':
                    delete_row = True
                else:
                    if '&nbsp;' in cell and not delete_row:
                        cell = cell.replace('&nbsp;', ' ')
                        # cell.content = cell_html
                    # print(cell)
            # Delete empty rowns
            if delete_row:
                row.decompose()
            else:
                html_temp += (
                    u'<tr style="font-size:14px">'
                    u'<td style="width:173">{0}:</td>'
                    u'<td style="width:717">{1}</td>'
                    u'</tr>').format(
                        row.select_one(
                            'td:nth-of-type(1)').get_text(strip=True),
                        row.select_one(
                            'td:nth-of-type(2)').get_text(strip=True)
                )
        html_temp += u'</tbody></table><br>'
        checksum = md5.md5(html_temp.encode('utf8')).hexdigest()
        if checksum in previouslySent:
            # hvis lektien tidligere er sendt og har due-date i dag,
            # så undlad at sende
            if re.match(r'^\D+, \d+\. \D+\. \d+:', header):
                # Måned angivet som forkortelse
                ft = '%A, %d. %b. %Y:'
            else:
                # Måned angivet fuldt ud ("Maj")
                ft = '%A, %d. %b %Y:'
            if datetime.strptime(header, ft).date() == datetime.today().date():
                continue
        homework_checksums.add(checksum)
        html_temp += html
        html = html_temp
    if homework_checksums.issubset(previouslySent):
        return '', ''
    else:
        return(html, homework_checksums)


def getHomework(cname, url):
    bs = surllib.skoleGetURL(url, True, noCache=True)
    return formatHomework(cname, bs)


@config.Section(SECTION)
def skoleHomework(cname):
    'Lektier'
    config.clog(cname, u'Kigger efter nye lektier')
    url = schildren.getChildURL(cname, 'item/weeklyplansandhomework/diary/')

    bs = surllib.skoleGetURL(url, True, noCache=True)

    li = bs.find_all('li', 'ccl-rwgm-column-1-2 sk-grid-priority-column')

    if li:
        for item in li:
            for a in item.find_all('a', href=True):
                url = a['href']
                bs = surllib.skoleGetURL(url, True, noCache=True)
                url = bs.find('a', id='sk-diary-notes-view-all', href=True)
                url['href'] = url['href'] + '/NextMonth'
                homework, homework_checksums = getHomework(cname, url['href'])
                if homework and homework_checksums:
                    wid = url['href'].split('/')[-1]  # e.g. 35-2018
                    title = bs.find('h3').text.strip()
                    msg = semail.Message(cname, SECTION, unicode(homework))
                    msg.setTitle(unicode(title))
                    msg.setMessageID(wid)
                    msg.setData(list(homework_checksums))
                    msg.maybeSend()
    else:
        if u'ikke autoriseret' in bs.text:
            config.clog(cname, u'Din skole bruger ikke lektier. '
                        u"Du bør bruge '--section ,-%s'" % SECTION)
