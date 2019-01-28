# -*- coding: utf-8 -*-
#
# The special page with
#     Bekræft kontaktoplysninger
# is only shown rarely, e.g., at first login, every N months
#
# skoleConfirm is called from surllib

import sbs4
import semail


def skoleConfirm(bs):
    '''Send e-mail wrt confirmation of your own contact details
Do not actually click the confirm link. This is done in surllib.'''

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

    sbs4.extract(form, 'script,div.ccl-formbuttonspanel')
    sbs4.unwrap(form, 'label,legend,fieldset')
    for tag in form.select('*'):
        del tag['class']
    for ol in form.select('ol'):
        ol.name = 'div'
        ol['style'] = 'margin:10px 0'

    form.name = 'div'
    for att in list(form.attrs):
        del form[att]
    sbs4.appendTodayComment(form)

    msg = semail.Message(cnames[0], 'con', unicode(form))
    for cname in cnames[1:]:
        msg.addChild(cname)
    msg.setTitle(bs.h2.text)
    msg.maybeSend()
