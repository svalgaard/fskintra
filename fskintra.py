#!/usr/bin/env python
# -*- coding: utf-8 -*-

import skoleintra.config
import skoleintra.schildren
import skoleintra.pgFrontpage
import skoleintra.pgContacts
import skoleintra.pgDialogue
import skoleintra.pgDocuments

cnames = skoleintra.schildren.getChildren()

skoleintra.pgFrontpage.skoleFrontpage(cnames)
skoleintra.pgDialogue.skoleDialogue(cnames)

for cname in cnames:
    skoleintra.pgContacts.skoleContacts(cname)
    skoleintra.pgDocuments.skoleDocuments(cname)
