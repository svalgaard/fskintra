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

* Linux, FreeBSD
* Working mail server answering on localhost port 25
* Python 2.5+ (not 3.x)
* Python libraries: mechanize (0.2.5), BeautifulSoup (3.2.x)

You can get the required Python libraries in Ubuntu by running:

	apt-get install python-beautifulsoup python-mechanize

The default packages in Ubuntu 12.04 works.

HOWTO
=====

Setup
-----

Run the following command, and answer the questions

	fskintra.py --config

Next, test this by running the actual script

	fskintra.py

Your configuration is saved in ~/.skoleintra/skoleintra.txt
Further, ~/.skoleintra contains a cache of fetched content and sent emails.

Cron-job
--------

Add the following to your crontab file to make it run twice daily

	25 6,18 * * * /path/to/fskintra.py -q

By adding -q you only get an email, if there is something interesting to see.

Problems?
---------

The current version of fskintra is not very good at handling http errors. If an error occurs, you can usually fix this by simply run the script again. If this is not enough, you can add the parameter -v to get more information on why the error occured:

	fskintra.py -v


Author
======

fskintra is maintained by Jens Svalgaard kohrt - http://svalgaard.net/jens/ - github AT svalgaard.net
