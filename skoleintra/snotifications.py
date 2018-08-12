# -*- coding: utf-8 -*-
#
#

import config
import surllib
import datetime

DT_FORMAT = '%Y.%m.%d-%H.%M.%S.%f'


def checkForUpdates():
    now = datetime.datetime.now()

    bs = surllib.skoleGetURL(
        '/notifications/v1?useNewerThan=False&pageSize=10', True, True)

    # Find lastUpdateURL
    links = bs.select('.sk-notifications-list li a')
    if links and links[0].has_attr('href'):
        updateURL = links[0]['href']
        config.log(u'Sidste opdatering var til %s' % updateURL, 2)
    else:
        updateURL = None
        config.log(u'Kunne ikke finde sidst opdaterede side', 2)

    state = (now, updateURL)

    # Should we do a full check?
    br = surllib.getBrowser()

    if br.getState('lastUpdateURL') != updateURL:
        # New top update
        config.log(u'Kører fuld opdatering: Forventer nyt opslag/besked', 1)
        return (True, state)

    try:
        lut_ = br.getState('lastUpdateTime')
        lut = datetime.datetime.strptime(lut_, DT_FORMAT) if lut_ else None
    except ValueError:
        lut = None

    if not lut or now < lut:
        # lastUpdateTime is somehow wrong
        config.log(u'Kører fuld opdatering: Mangler tidsstempel fra '
                   u'sidste kørsel', 1)
        return (True, state)

    # Do a daily full check the first time we are accessed after 05:00
    pit = now.replace(hour=5, minute=0, second=0, microsecond=0)
    if now.hour < 5:
        # Between midnight and 05:00, go back one day
        pit -= datetime.timedelta(1)
    if lut <= pit:
        # Last update was before
        config.log(u'Kører fuld opdatering: Første kørsel i dag', 1)
        return (True, state)

    # Did we NOT run this with the --quick parameter
    if config.options.fullupdate:
        config.log(u'Kører fuld opdatering selvom der ikke forventes '
                   u'nyt. Du bør bruge --quick', 1)
        return (True, state)

    # No need to run a full update
    config.log(u'Kører ikke fuld opdatering - der forventes intet nyt', 1)
    return (False, state)


def saveState(state):
    (now, updateURL) = state

    br = surllib.getBrowser()

    if now:
        br.setState('lastUpdateTime', now.strftime(DT_FORMAT))
    if updateURL:
        br.setState('lastUpdateURL', updateURL)
    br.saveState()
