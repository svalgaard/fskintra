ForældreIntra til Email
=======================

ForældreIntra er en del af SkoleIntra, der brugers af næsten alle
danske folkeskoler til kommunikation mellem skole og hjem. fskintra
logger på ForældreIntra og konverterer indholdet til almindelige
emails. Du vil bl.a. modtage en email, hver gang der kommer nyt et af
flg. steder:

* Forsiden: Nyheder på opslagstavlen inkl. fødselsdage
* Dialog/beskeder: Nye beskeder (både sendt og modtaget)
* Arkiv/dokumenter: Nye dokumenter

Alle emails bliver gemt, dvs. du får kun en email, såfremt der faktisk
er kommet nyt.

NB: Ny version
--------------

Juli 2018: Denne version af fskintra bruger (modsat den tidligere) det nye
design af ForældreIntra hjemmesiden.

Nyeste version kan p.t. findes her:

    # Til ForældreIntra med nyt design
    https://github.com/svalgaard/fskintra/tree/nyt.design
    # Til ForældreIntra Classic
    https://github.com/svalgaard/fskintra

Når det har kørt i et stykke tid, skiftes over, så denne version bliver
"standard versionen" og den gamle fskintra skal findes i en undermappe.

Eksempel
========

Som standard tilbyde ForældreIntra at sende dig en email hvis der er
nye beskeder eller andet, men du får kun overskriften/første linje af
beskeden - nogle gange endda kun, hvem der har skrevet den:

<pre>
> Advisering om nyt i ForældreIntra - Dinoskolen:
>
> ForældreIntra for 3.a:
> *Besked*    Besked fra Peter Nielsen [Åbn]
>
> Klik her for at komme til ForældreIntra.
</pre>

Med fskintra får du i stedet en email med selve indholdet af beskeden
og behøver ikke længere at logge på, for at se, hvad der står

<pre>
> Hvor er Annas sorte højregummistøvle?
>
> Fra: Peter Nielsen (Anna 3.a)
> Til: Anders Andersen (Bjarke 3.a), m.fl.
> Dato: 07-09-2013 12:14:16
>
> Anna kan ikke finde sin ene sorte gummistøvle - og får nu våde fødder.
>
> Kan du finde den? Vi/Anna giver en lakrids, hvis den bliver fundet og
> bragt til hende i 3.a.
>
> Mvh, Peter Nielsen
</pre>

Krav
====

* Python 2.7.x (ikke 3.x!)
* Pythonpakker: mechanize (0.3.x), BeautifulSoup (4.x), lxml (4.x)

Du kan få de krævede pythonpakker i Ubuntu 18.04 ved at køre

    user@sputnik:~$ sudo apt install python python-pip python-lxml python-bs4
    user@sputnik:~$ sudo pip2 install mechanize

NB: Mechanize pakken findes i Ubuntu, men kun i version 0.2.x.

Alternativt kan du bruge pip:

    # Check først at det er pip til Python 2.x du bruger:
    user@sputnik:~$ pip -V
    pip 10.0.1 from /.../pip (python 2.7)

    user@sputnik:~$ sudo pip install lxml beautifulsoup4 mechanize


HOWTO
=====

Opsætning
---------

Hent de krævede pythonpakker (se ovenfor). Dernæst hentes nyeste
version af programmet fra nedenstående side - fx ved at hente
zip-filen, eller endnu bedre ved at bruge git

    https://github.com/svalgaard/fskintra/tree/nyt.design

Kør følgende kommando, og besvar spørgsmålene

    ./fskintra.py --config

Til slut testes programmet ved at køre det

    ./fskintra.py

Din opsætning gemmes i $HOME/.skoleintra/skoleintra.txt. Såfremt du
kun skal rette lidt kan det evt. være smartest at rette direkte i
filen i stedet for at køre --config igen.

I $HOME/.skoleintra/ gemmes også alt hentet indhold og alle sendte
emails.

Cron-job
--------

Tilføj flg. linje til din crontab fil for at få programmet til at køre
to gange dagligt:

    PYTHONIOENCODING=UTF-8
    25 6,18 * * * /path/to/fskintra.py -q

Ved at tilføje -q, får du kun en email, såfremt der er noget
interessant at se (og ikke en email om, at fskintra har prøvet at
finde noget nyt uden at gøre det).

Linjen med PYTHONIOENCODING=UTF-8 er ikke altid nødvendig (se evt. nedenfor),
men er næsten altid en god idé.

Problemer?
----------

**UnicodeEncodeError**
I nogle situationer giver Python desværre en unicode-fejl lignende følgende

    Traceback (most recent call last):
      File "/home/user/fsk/fskintra.py", line 12, in <module>
        cnames = skoleintra.schildren.skoleGetChildren()
      File "/home/user/fsk/skoleintra/schildren.py", line 22, in skoleGetChildren
        config.log(u'Henter liste af bM-CM-8rn')
      File "/home/user/fsk/skoleintra/config.py", line 185, in log
        sys.stderr.write(u'%s\n' % s)
    UnicodeEncodeError: 'ascii' codec can't encode character u'\xf8' in position 17: ordinal not in range(128)

En løsning vil i næsten alle tilfælde være at sætte miljøvariablen
PYTHONIOENCODING til UTF-8.

Hvis du bruger bash eller lignende (hvis du ikke ved, om du gør, så gør
du sikkert).

    export PYTHONIOENCODING=UTF-8
    /sti/til/fskintra

Hvis du bruger tcsh eller lignende:

    setenv PYTHONIOENCODING UTF-8
    /sti/til/fskintra

**HTTP/HTML fejl**
Den nuværende version af fskintra er ikke altid god til at håndtere
http/html fejl. Hvis der sker en fejl, kan du for det meste løse
problemet ved at køre fskintra igen. Hvis det ikke er nok, kan du
evt. tilføje parameteren -v for muligvis at se mere om, hvad der går
galt:

    fskintra.py -v

Du er evt. også velkommen til at kontakte mig. Såfremt det ikke
virker, må du meget gerne vedhæfte hvad der bliver skrevet, når
fskintra.py køres med -v.

Hvem?
=====

fskintra er skrevet/opdateres af
Jens Svalgaard kohrt - http://svalgaard.net/jens/ - github AT svalgaard.net

Ændringer og forslag er bl.a. kommet fra
* Jacob Kjeldahl, https://github.com/kjeldahl
* Michael Legart, https://github.com/legart
* Kasper Lund
* Jesper Rønn-Jensen, https://github.com/jesperronn
* Benny Simonsen, https://github.com/bennyslbs
