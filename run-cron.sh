#! /bin/bash
#
# Ret evt. nedenstående fil til fx. cronjobs såfremt du har brug for en
# særlig version af python m.v.
#

ROOT="$(dirname "$0")"
cd "$ROOT"

python ./fskintra.py
