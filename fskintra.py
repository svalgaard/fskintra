#! /usr/bin/env python
#
#
#

import skoleintra.config
import skoleintra.pgDialogue
import skoleintra.pgFrontpage
import skoleintra.schildren

cnames = skoleintra.schildren.skoleGetChildren()

for cname in cnames:
    skoleintra.schildren.skoleSelectChild(cname)

    skoleintra.pgFrontpage.skoleFrontpage()
    skoleintra.pgDialogue.skoleDialogue()
