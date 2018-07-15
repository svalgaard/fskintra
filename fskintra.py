#!/usr/bin/env python
# -*- coding: utf-8 -*-

import skoleintra.config
import skoleintra.schildren
import skoleintra.snotifications
import skoleintra.pgFrontpage
import skoleintra.pgContacts
import skoleintra.pgDialogue
import skoleintra.pgDocuments
import skoleintra.pgPhotos
import skoleintra.pgSignup


def main():
    (full, state) = skoleintra.snotifications.checkForUpdates()
    if not full:
        return

    cnames = skoleintra.schildren.getChildren()

    skoleintra.pgFrontpage.skoleFrontpage(cnames)
    skoleintra.pgDialogue.skoleDialogue(cnames)

    for cname in cnames:
        skoleintra.pgContacts.skoleContacts(cname)
        skoleintra.pgDocuments.skoleDocuments(cname)
        skoleintra.pgPhotos.skolePhotos(cname)
        skoleintra.pgSignup.skoleSignup(cname)

    # save updated state
    skoleintra.snotifications.saveState(state)


if __name__ == '__main__':
    main()
