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


def main(argv=None):
    skoleintra.config.parseArgs(argv)

    (full, state) = skoleintra.snotifications.checkForUpdates()
    if not full:
        return

    cnames = skoleintra.schildren.getChildren()

    # Sections/pages are considered in the order they were imported
    for sf in skoleintra.config.PAGE_SECTIONS:
        sf.maybeRun(cnames)

    # save updated state
    skoleintra.snotifications.saveState(state)


if __name__ == '__main__':
    main()
