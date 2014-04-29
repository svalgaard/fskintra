#! /usr/bin/env python
#
#
#

import skoleintra.config
import skoleintra.pgDialogue
import skoleintra.pgDocuments
import skoleintra.pgFrontpage
import skoleintra.pgWeekplans
import skoleintra.schildren

cnames = skoleintra.schildren.skoleGetChildren()
for cname in cnames:
    skoleintra.schildren.skoleSelectChild(cname)

    skoleintra.pgFrontpage.skoleFrontpage()
    skoleintra.pgDialogue.skoleDialogue()
    skoleintra.pgDocuments.skoleDocuments()
    skoleintra.pgWeekplans.skoleWeekplans()
