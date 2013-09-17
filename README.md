Forældreintra til Email
=======================

Dette program logger på ForældreIntra (en del af SkoleIntra, der
brugers af næsten alle danske folkeskoler) og konverterer indholdet
til emails. Du vil bl.a. modtage emails, hver gang der kommer ny

* Forsiden: Nyheder på opslagstavlen
* Forsiden: Nyt forside billede, skema, osv.
* Dialog/beskeder: Nye beskeder (både sendt og modtaget)
* Arkiv/dokumenter: Nye dokumenter

Alle emails bliver gemt, dvs. du får kun en email, såfremt der er kommet nyt.

Eksempel
========

Som standard tilbyde ForældreIntra at sende dig en email hvis der er
nye beskeder eller andet, men du får kun overskriften/første linje af
beskeden - nogle gange endda endnu mindre:

<pre>
> Advisering om nyt i ForældreIntra - Dinoskolen:
>
> 4.a:
> *Besked*    Besked fra Peter Nielsen
>
> Klik for at åbne ForældreIntra eller MobilIntra.
</pre>

Med fskintra får du i stedet selve indholdet i beskeden og behøver
ikke længere at logge på, for at se, hvad der står

<pre>
> Hvor er Annas sorte højregummistøvle?
>
> Fra: Peter Nielsen (Anna 3.a)
> Til: Anders Andersen (Bjarke 3.a), m.fl.
> Dato: 07-09-2013 12:14:16
>
> Anna kan ikke finde sin ene sorte gummistøvle - og får nu våde fødder.
>
> Kan du finde den? Vi/Anna giver en lakrids, hvis den bliver fundet og bragt til hende i 3.a
>
> Mvh, Peter Nielsen
</pre>

Krav
====

* Linux, FreeBSD
* Python 2.5+ (ikke 3.x)
* Pythonpakker: mechanize (0.2.5), BeautifulSoup (3.2.x)

Du kan få de krævede pythonpakker i Ubuntu ved at køre

    sudo apt-get install python-beautifulsoup python-mechanize

Pakkerne i standard Ubuntu 12.04 virker.

HOWTO
=====

Opsætning
---------

Hent nyeste version af programmet fra denne side - fx ved at hente
zip-filen, eller endnu bedre ved at bruge git

    https://github.com/svalgaard/fskintra

Kør følgende kommando, og besvar spørgsmålene

    fskintra.py --config

Dernæst, test programmet ved at køre det

    fskintra.py

Din opsætning gemmes i $HOME/.skoleintra/skoleintra.txt.
I $HOME/.skoleintra gemmes også alt hentet indhold og alle sendte emails.

Cron-job
--------

Tilføj flg. linje til din crontab fil for at få programmet til at køre
to gange dagligt:

    25 6,18 * * * /path/to/fskintra.py -q

Ved at tilføje -q, får du kun en email, såfremt der er noget
interessant at se (og ikke en email om, at fskintra har prøvet at
finde noget nyt uden at gøre det).

Problemer?
----------

Den nuværende version af fskintra er ikke særlig god til at håndtere
http fejl. Hvis der sker en fejl, kan du for det meste løse problemet
ved at køre programmet igen. Hvis det ikke er nok, kan du evt. tilføje
parameteren -v for mulighed at se mere om, hvad der går galt:

    fskintra.py -v

Du er evt. velkommen til at kontakte mig. Såfremt det ikke virker, må
du meget gerne vedhæfte hvad der bliver skrevet, når fskintra.py køres
med -v.

Author
======

fskintra er skrevet/opdateres af
Jens Svalgaard kohrt - http://svalgaard.net/jens/ - github AT svalgaard.net
