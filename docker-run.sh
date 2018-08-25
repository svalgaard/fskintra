#! /bin/bash
#
# Used to run fskintra inside docker.
# See Docker.md for details
#
# Your fskintra details are saved in ~/.skoleintra
#

docker run \
    --rm \
    -it \
    -v ~/.skoleintra:/root/.skoleintra \
    -t fskintra \
    "$@"
