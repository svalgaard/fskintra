ForældreIntra til Email
=======================

ForældreIntra er en del af SkoleIntra, der brugers af næsten alle danske folkeskoler til kommunikation mellem skole og hjem. ```fskintra``` logger på ForældreIntra og konverterer indholdet til almindelige emails. Du vil bl.a. modtage en email, hver gang der kommer nyt et af flg. steder:

* Forsiden: Nyheder på opslagstavlen inkl. fødselsdage
* Beskeder (både sendt og modtaget)
* Dokumenter
* Billeder
* Samtaler

Alle emails bliver gemt, dvs. du får kun en email, såfremt der faktisk er kommet nyt.

NB: Ny version
--------------

Juli/August 2018: Denne version af fskintra bruger (modsat den tidligere) det nye design af ForældreIntra hjemmesiden. Endvidere kan man bruge uni-login til at logge ind og ikke kun "skole-specifikt/almindeligt" logind.

Nyeste version kan p.t. findes her:

    # Til ForældreIntra med nyt design
    https://github.com/svalgaard/fskintra/tree/nyt.design
    # Til ForældreIntra Classic
    https://github.com/svalgaard/fskintra

Når det har kørt i et stykke tid, skiftes over, så denne version bliver "standardversionen".

Medmindre du selv har lyst til at kigge på Python kode, bør du nok vente lidt med at skifte over til at bruge den nye version lidt endnu.

Eksempel
========

Som standard tilbyde ForældreIntra at sende dig en email hvis der er nye beskeder eller andet, men du får kun overskriften/første linje af beskeden - nogle gange endda kun, hvem der har skrevet den:

```
> Advisering om nyt i ForældreIntra - Dinoskolen:
>
> ForældreIntra for 3.a:
> *Besked*    Besked fra Peter Nielsen [Åbn]
>
> Klik her for at komme til ForældreIntra.
```

Med fskintra får du i stedet en email med selve indholdet af beskeden
og behøver ikke længere at logge på, for at se, hvad der står

```
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
```

Hvordan?
========

Se i underkataloget ```docs``` for information om, hvordan du installerer ```fskintra```.


Hvem?
=====

fskintra er skrevet/opdateres af
[Jens Svalgaard kohrt](http://svalgaard.net/jens/) - github AT svalgaard.net

Ændringer og forslag er bl.a. kommet fra
* [Jacob Kjeldahl](https://github.com/kjeldahl)
* [Michael Legart](https://github.com/legart)
* Kasper Lund
* [Jesper Rønn-Jensen](https://github.com/jesperronn)
* [Benny Simonsen](https://github.com/bennyslbs)
