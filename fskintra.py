#!/usr/bin/env python
# -*- coding: utf-8 -*-

import skoleintra.config
import skoleintra.pgContactLists
import skoleintra.pgDialogue
import skoleintra.pgDocuments
import skoleintra.pgFrontpage
import skoleintra.pgWeekplans
import skoleintra.schildren

cnames = skoleintra.schildren.getChildren()

skoleintra.pgFrontpage.skoleFrontpage(cnames)
skoleintra.pgDialogue.skoleDialogue(cnames)

for cname in cnames:
    pass

    # PENDING for new design
    # skoleintra.pgContactLists.skoleContactLists()
    # skoleintra.pgDocuments.skoleDocuments()
    # skoleintra.pgWeekplans.skoleWeekplans()
