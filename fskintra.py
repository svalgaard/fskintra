#!/usr/bin/env python
# -*- coding: utf-8 -*-

import skoleintra.config
import skoleintra.schildren
import skoleintra.pgFrontpage
import skoleintra.pgDialogue
# PENDING for new design
# import skoleintra.pgContactLists
import skoleintra.pgDocuments
# import skoleintra.pgWeekplans

cnames = skoleintra.schildren.getChildren()

#skoleintra.pgFrontpage.skoleFrontpage(cnames)
#skoleintra.pgDialogue.skoleDialogue(cnames)

for cname in cnames:
    skoleintra.pgDocuments.skoleDocuments(cname)

    # PENDING for new design
    # skoleintra.pgContactLists.skoleContactLists()
    # skoleintra.pgWeekplans.skoleWeekplans()
