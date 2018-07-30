# -*- coding: utf-8 -*-
#
# The special page with
#     Bekræft kontaktoplysninger
# is only shown at first login
# skoleConfirm is called from surllib

import semail
import time
import bs4


def skoleConfirm(bs):
    '''Send e-mail wrt confirmation of your own contact details
Do not actually click the confirm link'''
    forms = bs.select('.sk-l-content-wrapper form')
    assert(forms)
    form = forms[0]
    assert(form['action'].endswith('Confirm'))

    # Find name(s) of children
    #
    cnames = []
    for li in form.select('li'):
        st = li.text
        s = st.split() if st else []
        if len(s) >= 2 and s[0].lower().startswith('elev:'):
            cnames.append(unicode(s[1]))
    if not cnames:
        cnames.append('fskintra')

    for li in form.select('li'):
        li.name = 'p'
        li['style'] = 'margin: 0;'
    for ol in form.select('ol'):
        ol.name = 'p'

    for sel in 'script,div.ccl-formbuttonspanel'.split(','):
        for kill in form.select(sel):
            kill.extract()
    for sel in 'a,label,a,legend,fieldset'.split(','):
        for uw in form.select(sel):
            uw.unwrap()

    form.name = 'div'
    for att in list(form.attrs):
        del form[att]
    form.append(bs4.Comment(' I dag er %s ' % time.strftime(u'%d. %b. %Y')))

    msg = semail.Message(cnames[0], 'con', unicode(form))
    for cname in cnames[1:]:
        msg.addChild(cname)
    msg.setTitle(bs.h2.text)
    msg.maybeSend()
