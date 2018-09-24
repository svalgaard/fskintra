# -*- coding: utf-8 -*-

import bs4
import copy as _copy
import re
import sys
import time

import config


def copy(bs):
    'Return a copy of bs'
    return _copy.copy(bs)


def extract(bs, sel):
    'Extract (delete tags incl. contents) elements matching sel'
    for elm in list(bs.select(sel)):
        elm.extract()


def unwrap(bs, sel):
    'Unwrap (delete tags excl. contents) elements matching sel'
    for elm in list(bs.select(sel)):
        elm.unwrap()


def find1orFail(bs, sel, asText=False):
    'Find a single tag matching sel or fail'
    hits = bs.select(sel)
    if len(hits) != 1:
        config.log(u"'%s' var %d gange på siden (!=1)" % (sel, len(hits)), -1)
        sys.exit(1)
    hit = hits[0]
    if asText:
        hit = hit.text.strip()
    return hit


def contents2html(bs):
    'Return HTML inside bs as unicode text'
    return u''.join(unicode(c) for c in bs.contents).strip()


def appendComment(bs, text=''):
    '''Append a comment 'Tag' with the specified text'''
    bs.append(bs4.Comment(text))


def appendTodayComment(bs):
    '''Append a comment 'Tag' with today's date'''
    appendComment(bs, time.strftime(u' I dag er %Y-%m-%d '))


def deobfuscateEmail(s):
    'Deobfuscate an e-mail address. Return the address if possible o.w. None'
    if len(s) % 2 or not s:
        # Not with a length divible by 2
        return
    try:
        # Check that this is a hex string
        int(s, 16)
    except ValueError:
        # Not hex string somewhere
        return
    key = int(s[:2], 16)
    mail = ''.join(chr(int(s[i:i+2], 16) ^ key) for i in range(2, len(s), 2))
    if '@' not in mail:
        return  # not an e-mail
    return mail


def cleanupSoup(bs):
    '''Cleanup/deobfuscate the soup'''

    # deobfuscate content/spans with email addresses
    CLASS = '__cf_email__'
    DATA = 'data-cfemail'
    HREF_PREFIX = '/cdn-cgi/l/email-protection'
    for tag in bs.find_all(**{'class': CLASS, DATA: re.compile('.')}):
        email = deobfuscateEmail(tag[DATA])
        if email:
            del tag[DATA]
            tag['class'].remove(CLASS)
            tag.string = email
            if tag.name == 'span' and tag.attrs == {}:
                tag.unwrap()
            if tag.name == 'a' and tag.has_attr('href') and \
                    tag['href'].startswith(HREF_PREFIX):
                tag['href'] = 'mailto:' + email

    # deobfuscate href's with email links
    for tag in bs.find_all('a', href=re.compile('^%s.*' % (HREF_PREFIX))):
        href = tag['href']
        email = deobfuscateEmail(href[len(HREF_PREFIX):].strip('#'))
        if email:
            tag['href'] = 'mailto:' + email
        else:
            tag.unwrap()

    BLOCKED = 'blocked::'
    for tag in bs.find_all('a', title=re.compile('^%s.*' % BLOCKED)):
        tag['title'] = tag['title'][len(BLOCKED):]
        if tag.has_attr('href') and tag['title'] == tag['href']:
            del tag['title']

    # Remove imgs without an actual image - probably copied into ForældreIntra
    # from e.g., Outlook.
    rec = re.compile('^(%s).*' % '|'.join(['cid']))
    for img in bs.find_all('img', src=rec):
        img.extract()

    # Clean up "Word-like" style attributes
    for tag in bs.find_all():
        if not tag.has_attr('style'):
            continue
        sts = []
        for st in tag['style'].split(';'):
            st = st.strip()
            if st.startswith('mso-'):
                continue
            if st:
                sts.append(st)
        if sts:
            tag['style'] = u';'.join(sts)
        else:
            del tag['style']

    # Remove target from links
    for tag in bs.select('a'):
        del tag['target']

    # Remove empty class attributes
    for tag in bs.find_all(**{'class': ''}):
        if not tag.has_attr('class'):
            continue
        while '' in tag['class']:
            tag['class'].remove('')
        if not tag['class']:
            del tag['class']


def trimSoup(bs):
    '''Trim "body" of bs for whitespace including <br/>'''
    for rev in [False, True]:
        children = list(bs.children)
        if rev:
            children = reversed(children)
        for c in children:
            if isinstance(c, bs4.element.Tag):
                if c.name == 'br':
                    c.extract()
                    continue
            if isinstance(c, bs4.element.NavigableString):
                text = c.string
                text = text.rstrip() if rev else text.lstrip()
                if not text:
                    c.extract()
                    continue
                c.string.replace_with(text)
            break


def condenseSoup(bs):
    '''Trim bs for empty divs, etc to condense the HTML put in e-mails'''
    for e in bs.select('div'):
        # remove empty divs
        contents = u''.join(map(unicode, e.children)).strip()
        if not contents:
            e.extract()

    trimSoup(bs)

    for c in list(bs.descendants):
        if isinstance(c, bs4.element.NavigableString) and \
                c.previous_sibling and \
                isinstance(c.previous_sibling, bs4.element.NavigableString):
            text = c.previous_sibling.string + c.string
            c.previous_sibling.string.replace_with(text)
            c.extract()


def beautify(data):
    bs = bs4.BeautifulSoup(data, 'lxml')
    cleanupSoup(bs)
    return bs
