# -*- coding: utf-8 -*-

import sys

#
# Check that we have Python 2.7.x
#
if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    sys.exit(u'''fskintra kræver Python 2.7.x
Du kører med version %s
Måske har du flere Python-versioner installeret?''' % sys.version.split()[0])
