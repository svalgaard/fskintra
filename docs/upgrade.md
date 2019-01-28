# Opgradering #

Når der kommer ny version af ```fskintra``` kan opgradering ske i tre trin:


## 1. Hent alt nuværende indhold ##

Kør ```fskintra``` for at sikre dig at alt nuværende indhold er hentet:

```console
user@sputnik:~/fskintra$ ./fskintra.py
```


## 2. Opdater selve fskintra ##

Hvis du har hentet ```fskintra``` som en zip-fil, henter du blot en ny og
pakker den ud oven på den gamle version.

Hentede du ```fskintra``` vha. git, bruges git til at opdatere:

```console
user@sputnik:~/fskintra$ git pull
```


## 3. Nulstil at alt indhold er hentet ##

Såfremt måden indhold hentes eller formatet af e-mails ændret i den nye
version, kan du risikere at modtage en masse e-mails om noget der faktisk
ikke er en opdatering.
Det er derfor smart at køre ```fskintra``` med ```--catch-up``` for at
nulstille at alt indhold er hentet.

```console
user@sputnik:~/fskintra$ ./fskintra.py --catch-up
```

Bemærk at indhold, der er kommet ind på ForældreIntra i tidsrummet mellem
trin 1 og 3, i så fald ikke vil blive udsendt som e-mail.
