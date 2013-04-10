Forældreintra to Email
======================

This program logs into ForældreIntra (part of SkoleIntra) and converts the content inside to emails. This includes:

* Front page: Notices on the bulletin board (opslagstavle)
* Front page: Cover pictures
* ...
* Messages: "Emails" send inside the system to/from yourself

Everything is cached, i.e., you only get an email, if there are any new messages, etc.

Requirements
============

* Linux (probably)
* Working mail from the command line (i.e., sendmail me@example.com should send an email to me@example.com )
* Python 2.5+ (not 3.x)
* Python libraries: mechanize, BeautifulSoup

You can get the required Python libraries in Ubuntu by running:

	apt-get install python-beautifulsoup python-mechanize

HOWTO
=====

Setup
-----

Run the following command, and answer the questions

	fskintra.py --config

Next, test this by running the actual script

	fskintra.py

Cron-job
--------

Add the following to your crontab file to make it run twice daily

	25 6,18 * * * /path/to/fskintra.py -q

By adding -q you only get an email, if there is something interesting to see.
