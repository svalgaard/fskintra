#! /bin/bash
#
# Kopier nedenstående fil ned i samme katalog som fskintra.py og ret den
# til. Dette er smart til fx. cronjobs såfremt du har brug for en særlig
# version af python m.v.
#

# Sikr at Python kan finde ud af at lave UTF-8
export PYTHONIOENCODING=UTF-8

# Gå til samme bibliotek som denne fil ligger i
ROOT="$(dirname "$0")"
cd "$ROOT"

# Kør fskintra som default bruger
python ./fskintra.py --quiet --quick

# Kør fskintra som en anden bruger
# python ./fskintra.py --quiet --quick --profile ida
