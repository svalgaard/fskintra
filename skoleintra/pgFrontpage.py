#
# -*- encoding: utf-8 -*-
#

import config
import surllib
import semail
import re
import BeautifulSoup
import time

# special titles
TITLE_IGNORE = [u'Fælles nyheder',  # ignored (use RSS)
                u'Dialog mellem skole og hjem',  # extra menu (with flags)
                u'Information om klassen',  # ekstra menu
                u'Nyeste dokumenter',  # handled separately in pgDocuments
                ]
TITLE_COVERPIC = u'Forsidebillede'
TITLE_BBB = u'Klassens opslagstavle'
TITLE_NEWS = u'Nyt fra ...'

TEXT_I_CONFIRM = u'Jeg bekr\xe6fter, at oplysningerne er korrekte'


def _unwrap(bs):
    if 'childGenerator' not in dir(bs):
        return bs
    rs = list(bs.childGenerator())
    if len(rs) == 1:
        return _unwrap(rs[0])
    else:
        return rs


def _getTitle(bs):
    '''Titles on the front page are wrapped as this:

<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td valign="middle" align="left">
        <b>Forsidebillede</b><hr noshade="noshade" size="1" />
    </td>
  </tr>
</table>

i.e., a <table><tr><td> wrapping a <b> + <hr>
'''
    uw = _unwrap(bs)

    # The first tag must be a b and the second a hr
    # In some cases we might get a white space string before the <b><hr>
    uw = [e for e in uw if type(e) != BeautifulSoup.NavigableString or \
          e.string.strip()]

    if len(uw) != 2 \
            or uw[0].name != 'b' \
            or uw[1].name != 'hr':
        return None
    else:
        return uw[0].text


def skoleCoverPic(phtml):
    msg = semail.Message('frontpage', phtml)
    msg.setTitle(u'Nyt forsidebillede')
    msg.updatePersonDate()
    semail.maybeEmail(msg)


def skoleFrontBBB(phtml):
    msg = semail.Message('frontpage', phtml)
    txt = phtml.renderContents().decode('utf-8')
    txt = re.sub('<.*?>', ' ', txt)
    txt = re.sub('[ \n\t]+', ' ', txt)

    if u'har fødselsdag' in txt and u'Skrevet af' not in txt:
        # somebody's birthday
        msg.setTitle(txt)
        msg.setSender(txt.split(u' har ')[0].strip())
        msg.setDate(time.strftime('%d-%m-%Y'))
    else:
        txt = re.sub('<.*?>', ' ', txt)
        txt = re.sub('[ \n\t]+', ' ', txt)
        msg.setTitle(' '.join(txt.split()), True)
        msg.updatePersonDate()

    semail.maybeEmail(msg)


def skoleExamineNews(url, mid):
    bs = surllib.skoleGetURL(url, True)

    # title + main text
    title = bs.h3.text
    main = bs.findAll('table')[3].table

    # create msg
    msg = semail.Message(u'dialogue', main)
    msg.setMessageID(mid)
    msg.setTitle(title)
    msg.updatePersonDate()

    semail.maybeEmail(msg)


def skoleNewsFrom(bss):
    # /Infoweb/Fi/VisNytFra.asp?ID=97&Kat=2

    for bs in bss:
        if not bs.a or not bs.a['href']:
            continue  # ignore
        href = bs.a['href']
        mid = href.split('/')[-1].replace('.asp?ID=', '-').split('&')[0]
        # e.g. VisNytFra-97
        if not 'VisNytFra' in href:
            continue
        skoleExamineNews(href, mid)


def skoleOtherStuff(title, phtml):
    # some part of the frontpage, e.g., weekly schedule
    msg = semail.Message('frontpage', phtml)
    msg.setTitle(title)
    semail.maybeEmail(msg)


def skoleConfirmPersonalData(bs):
    # check that we actually have the right form

    txts = [
        u'Bekræft personoplysninger',
        u'Navn og adresse:',
        u'E-mailadresse',
        u'Fastnettelefon:',
        u'Mobiltelefon',
    ]
    e = False
    for txt in txts:
        if txt not in bs.text:
            config.log(u'Hmmm.. "%s" ikke fundet på bekræftigelsessiden...')
            e = True
    if e:
        return

    # Find first form, and first table inside the form
    f = bs.findAll('form')
    if f:
        bs = f[0]
    f = bs.findAll('table')
    if f:
        bs = f[0]

    msg = semail.Message('frontpage', bs)
    msg.setTitle(u'Bekræft personoplysninger')
    semail.maybeEmail(msg)

    # And now, click the button to confirm the details
    br = surllib.getBrowser()
    fs = [f for f in br.forms()]

    if len(fs) == 1 and fs[0].name == 'FrontPage_Form1':
        # we have one form!
        br.select_form(fs[0].name)

        ss = bs.findAll('input', type='submit')
        if len(ss) == 1 and ss[0]['value'] == TEXT_I_CONFIRM:
            config.log(u'Bekræfter personlige data')
            br.submit()  # click submit!
            return

    # something went wront above
    config.log(u'Hmmm.. "%s" ikke fundet på Bekræftigelsessiden...')


def skoleFrontpage():
    surllib.skoleLogin()

    config.log('Behandler forsiden')

    url = 'http://%s/Infoweb/Fi2/Forside.asp' % config.HOSTNAME
    data = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    br = surllib.getBrowser()
    aurl = br.geturl()
    if u'Personoplysninger.asp' in aurl:
        # We are actually asked to confirm our personal data
        config.log(u'Bekræfter først vores personlige data')
        skoleConfirmPersonalData(data)

        data = surllib.skoleGetURL(url, asSoup=True, noCache=True)

    # find main table
    maint = []
    for mt in data.findAll('table'):
        if mt.findParents('table') or mt.has_key('bgcolor'):
            continue
        maint.append(mt)
    assert(len(maint) == 1)  # assume exactly one main table

    maint = maint[0]

    # find interesting table tags
    itags = []
    for tag in maint:
        for ttag in tag.findAll('table'):
            if ttag.text:
                itags.append(ttag)

    g = []
    for itag in itags:
        t = _getTitle(itag)
        if t is None:
            # not a title
            assert(g is not None)  # the first MUST be a title
            g[-1][1].append(itag)
        else:
            # we have a new title
            g.append((t, []))

    for (t, xs) in g:
        ignore = len(xs) == 0 or t in TITLE_IGNORE
        config.log(u'Kategori [%s]%s' %
                   (t, ' (hoppes over)' if ignore else ''))
        if ignore:
            continue

        if t == TITLE_COVERPIC:
            assert(len(xs) == 1)  # exactly one cover picture
            skoleCoverPic(xs[0])
            continue
        elif t == TITLE_BBB:
            # BBB news are split
            # ignore first table which is a wrapper around all entries
            xs = xs[1:]
            map(skoleFrontBBB, xs)
        elif t == TITLE_NEWS:
            # News from...
            skoleNewsFrom(xs)
        else:
            # send msg if something has changed
            for x in xs:
                skoleOtherStuff(t, x)


if __name__ == '__main__':
    # test
    skoleFrontpage()
