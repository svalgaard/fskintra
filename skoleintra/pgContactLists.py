# -*- coding: utf-8 -*-

import config
import surllib
import semail

URL_MAIN = 'http://%s/Infoweb/Fi/Klasselister.asp' % config.HOSTNAME

# V1  = Navneliste
# V3a = Afkrydsningsliste
# V2  = Adresse- og telefonliste
# V4  = Elevernes e-mailadresser
# V8  = Elevernes fødselsdage
# V9  = Fotos af eleverne
# V5  = Kontaktoplysninger
# V6  = Forældres e-mailadresser
# V7  = Forældres profilbilleder
# V10 = Kontaktlærere
LISTS_TO_SEND = 'V5', 'V6'


def listsCheckList(postData, listtype):
    global bs, tbl
    # Fetch potential cached version
    bs = surllib.skoleGetURL(URL_MAIN, True, False, True, postData)

    if bs.cacheage > 6.9:
        bs = surllib.skoleGetURL(URL_MAIN, True, True, True, postData)

    tbl = bs.findAll('table')[2]
    if listtype == 'V6':
        # Remove links to pictures of parents
        for a in tbl.findAll('a'):
            a.replaceWithChildren()

    tr = tbl.find('tr')
    if tr.find('h2'):
        title = tr.find('h2').text
        tr.extract()
    elif tbl.find('h2'):
        title = tbl.find('h2').text
    else:
        title = u'Kontaktoplysninger'

    msg = semail.Message('contactList', tbl)
    msg.setTitle(title)
    semail.maybeEmail(msg)


def skoleContactLists():
    global bs, lists

    config.log(u'Kigger efter nye adresser')

    # read the initial page
    bs = surllib.skoleGetURL(URL_MAIN, True, False, True)

    # Setup post request
    postData = {}

    for inpd in [{'id': 'fSkjult'}, {'type': 'submit'}]:
        inp = bs.find('input', **inpd)
        if not inp:
            config.log(u'pgContactLists: INPUT med %s ej fundet' % repr(inpd))
            return
        postData[inp['name']] = inp['value']

    lists = None
    for sel in bs.findAll('select'):
        fst = sel.option['value']
        if sel['name'] in ['fKlasse', 'fSortering']:
            postData[sel['name']] = fst
        elif sel['name'] == 'R1':
            lists = sel
        else:
            # Unknown SELECT found
            config.log(u'pgContactLists: Ukendt SELECT: %s' % sel['name'])
            return

    if not lists:
        config.log(u'pgContactLists: SELECT med mulige lister ej fundet')
        return

    for opt in lists.findAll('option'):
        if opt['value'] in LISTS_TO_SEND:
            postData[lists['name']] = opt['value']
            listsCheckList(postData, opt['value'])


if __name__ == '__main__':
    # test
    skoleContactLists()
