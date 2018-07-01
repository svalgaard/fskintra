# -*- coding: utf-8 -*-

import config
import schildren
import semail
import surllib

MAX_CACHE_AGE = 6.9


def contactCard(cname, bs):
    # Find name
    name = bs.select('.sk-contact-person-name span.sk-labeledtext-value')
    assert(name)
    name = name[0].text.strip()

    # change all the divs+spans into a table
    for span in bs.findAll('span', 'sk-labeledtext-caption'):
        span.name = 'td'
        span['class'] = 'caption'
    for span in bs.findAll('span', 'sk-labeledtext-value'):
        span.name = 'td'
        span['class'] = 'value'
        span['style'] = 'font-weight: bold;'
    for div in bs.findAll('div', 'sk-labeledtext'):
        div.name = 'tr'
        del div['class']
    for h2 in bs.findAll('h2', 'title'):
        title = h2.text.strip()
        h2.name = 'tr'
        h2.string = ''
        h2.append(bs.new_tag(
            'td', colspan='2',
            style='font-weight: bold; font-size: 18px; padding-top: 12px'))
        h2.td.string = title
    for div in bs.findAll('div', 'section-block'):
        div.unwrap()
    for div in bs.findAll('div', 'section'):
        div.unwrap()
    for table in bs.findAll('div', 'text-block'):
        table.name = 'table'
    # Insert name of
    assert(table)  # If this fails, the design has changes drastically

    # we do now have two cases depending on whether the image is available
    img = bs.find('img')

    if img and 'placeholder' not in img['src']:
        # Image is here
        img['style'] = (
            'width: auto;'
            'height: auto;'
            'max-height: 200px;'
            'max-width: 200px;')
        table.wrap(bs.new_tag('td'))
        for div in bs.findAll('div', 'photo-block'):
            div.name = 'td'
            div['valign'] = 'top'
            div['style'] = 'padding-right: 15px;'
        body = bs.find('body')
        body.name = 'tr'
        body.wrap(bs.new_tag('table'))
        bs.table.wrap(bs.new_tag('body'))
    else:
        # Either no image or image-placeholder is used
        if img:
            img.decompose()
        div = bs.find('div', 'photo-block')
        if div:
            div.decompose()

    msg = semail.Message(u'contact', unicode(bs))
    msg.setTitle(name)
    msg.addChild(cname)
    msg.maybeSend()


def skoleContacts(cname):
    config.clog(cname, u'Kigger efter ny kontaktinformation')
    url = schildren.getChildURL(cname, '/contacts/students/cards')

    bs = surllib.skoleGetURL(url, True, MAX_CACHE_AGE)

    opts = bs.select('#sk-toolbar-contact-dropdown option')
    if not opts:
        config.clog(cname, u'Kan ikke finde nogen elever?')
        return

    for opt in opts:
        url = opt['value']
        bs2 = surllib.skoleGetURL(url, True, bs.cacheage + .01)

        contactCard(cname, bs2)
