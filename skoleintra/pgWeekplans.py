# -*- coding: utf-8 -*-

import config
import surllib
import schildren
import semail

SECTION = 'pln'

def formatWeekplan(bs):
    """Format the weekplan nicely for email"""
    weekplan = bs.find('div', "sk-weekly-plan-container")
    # Change into table
    table = weekplan.div
    table.name = 'table'
    # Remove a couple of unneeded tags
    for div in weekplan.find_all('div','sk-weekly-plan-grid'):
        div.unwrap()
    for ul in weekplan.find_all('ul', 'sk-weekly-plan-grid-row'):
        ul.unwrap()

    # li -> tr + wrap div content in td
    for li in weekplan.select('.sk-weekly-plan-header'):
        li.name = 'tr'
        # Clear attrobutes, so next loop can access ul in
        # li.sk-weekly-plan-grid-cell
        li.attrs = {}
        li.div.wrap(bs.new_tag('td'))

    # li -> tr + wrap ul content in td
    for li in weekplan.select('.sk-weekly-plan-grid-cell'):
        li.name = 'tr'
        li.attrs = {}
        li.ul.wrap(bs.new_tag('td'))

    # format
    for span in weekplan.select('.sk-weekly-plan-day'):
        span["style"] = 'display: block; font-weight: 600;'

    # format
    for span in weekplan.select('.sk-weekly-plan-date'):
        span['style'] = 'display: block;'

    # format
    for ul in weekplan.select('.sk-list'):
        ul['style'] = 'list-style-type:none;'

    return weekplan


def getWeekplan(cname, url):
    bs = surllib.skoleGetURL(url, True, noCache=True)
    return formatWeekplan(bs)



@config.Section(SECTION)
def skoleWeekplans(cname):
    'Ugeplaner'
    config.clog(cname, u'Kigger efter nye ugeplaner')
    url = schildren.getChildURL(cname, 'item/weeklyplansandhomework/list/')

    bs = surllib.skoleGetURL(url, True, noCache=True)
    ul = bs.find('ul', 'sk-weekly-plans-list-container')
    for a in ul.find_all('a', href=True):
        url = a['href']
        plan = getWeekplan(cname, url)
        wid = url.split('/')[-1] # e.g. 35-2018
        title = plan.find('h3').text.strip()

        if semail.hasSentMessage(tp=SECTION, mid=wid):
            continue
        else:
            msg = semail.Message(cname, SECTION, unicode(plan))
            msg.setTitle(title)
            msg.setMessageID(wid)
            msg.maybeSend()

