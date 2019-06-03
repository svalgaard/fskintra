# -*- coding: utf-8 -*-

import config
import schildren
import semail
import surllib


SECTION = 'hwk'


def formatHomework(bs):
    '''Format the homework nicely for email'''
    # Test if there is any homework
    if not bs.select('div.sk-white-box > b'):
        return ''
    html = u''

    for li in bs.select('ul.sk-list > li'):
        # Locate header with due-dates
        header = li.find('div', 'sk-white-box').b.text
        html += u'<b>{0}</b>'.format(header)
        html += u'<table border="1" cellpadding="1" cellspacing="1"><tbody>'
        # Locate each table with homework
        table = li.find('table')
        for row in table.select('tbody tr'):
            delete_row = False
            # Loop through each cell in the row
            for cell in row.find_all('td'):
                # Remove unneded tags
                if cell.find('span'):
                    cell.span.unwrap()
                del cell['style']
                if cell.encode_contents(formatter='html') == '&nbsp;':
                    delete_row = True
            # Delete empty rowns
            if delete_row:
                row.decompose()
            else:
                html += (
                    u'<tr style="font-size:14px">'
                    u'<td style="width:173">{0}:</td>'
                    u'<td style="width:717">{1}</td>'
                    u'</tr>').format(
                        row.select_one('td:nth-of-type(1)').string,
                        row.select_one('td:nth-of-type(2)').string
                    )
        html += u'</tbody></table><br>'

    return(html)


def getHomework(cname, url):
    bs = surllib.skoleGetURL(url, True, noCache=True)
    return formatHomework(bs)


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
                homework = getHomework(cname, url['href'])
                if homework:
                    wid = url['href'].split('/')[-1]  # e.g. 35-2018
                    # print(bs.prettify())
                    title = bs.find('h3').text.strip()
                    # print(homework)
                    msg = semail.Message(cname, SECTION, unicode(homework))
                    msg.setTitle(unicode(title))
                    msg.setMessageID(wid)
                    msg.maybeSend()
    else:
        if u'ikke autoriseret' in bs.text:
            config.clog(cname, u'Din skole bruger ikke lektier. '
                        u"Du bør bruge '--section ,-%s'" % SECTION)
