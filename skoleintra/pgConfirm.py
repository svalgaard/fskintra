# -*- coding: utf-8 -*-
#
# The special page with
#     Bekræft kontaktoplysninger
# is only shown at first login
# skoleConfirm is called from surllib

import semail
import surllib


def skoleConfirm(bs):
    '''Send e-mail wrt confirmation of your own contact details
Do not actually click the confirm link'''

    # 'decrypt' e-mail addresses
    surllib.deobfuscateSoup(bs)

    forms = bs.select('.sk-l-content-wrapper form')
    assert(forms)
    form = forms[0]
    assert(form['action'].endswith('Confirm'))

    # Find name(s) of children
    cnames = []
    for li in form.select('li'):
        st = li.text
        s = st.split() if st else []
        if len(s) >= 2 and s[0].lower().startswith('elev:'):
            cnames.append(unicode(s[1]))
            if len(s) >= 3:
                cnames[-1] += u' %s' % s[-1]
    if not cnames:
        cnames.append('fskintra')

    # Clean up HTML
    for li in form.select('li'):
        li.name = 'p'
        li['style'] = 'margin:0'

    for sel in 'script,div.ccl-formbuttonspanel'.split(','):
        for kill in form.select(sel):
            kill.extract()
    for sel in 'label,legend,fieldset'.split(','):
        for uw in form.select(sel):
            uw.unwrap()
    for tag in form.select('*'):
        del tag['class']
    for ol in form.select('ol'):
        ol.name = 'div'
        ol['style'] = 'margin:10px 0'

    form.name = 'div'
    for att in list(form.attrs):
        del form[att]
    form.append(surllib.todayComment())

    msg = semail.Message(cnames[0], 'con', unicode(form))
    for cname in cnames[1:]:
        msg.addChild(cname)
    msg.setTitle(bs.h2.text)
    msg.maybeSend()
