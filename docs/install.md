# Opsætning / Installation #

## Krav ##

* Python 2.7.x (ikke 3.x!)
* Pythonpakker: mechanize, BeautifulSoup, lxml (se punkt 2 nedenfor)
* Email-konto enten som smtp server hos dig selv eller fx. en Gmail konto

## 1. Hent fskintra ##

Hent de krævede pythonpakker (se ovenfor). Dernæst hentes nyeste version af programmet fra nedenstående side - fx ved at hente zip-filen og pakke den ud, eller endnu bedre ved at bruge git:

    user@sputnik:~$ git clone https://github.com/svalgaard/fskintra.git
    Cloning into 'fskintra'...
    remote: Counting objects: 415, done.
    remote: Total 415 (delta 0), reused 0 (delta 0), pack-reused 415
    Receiving objects: 100% (415/415), 102.68 KiB | 370.00 KiB/s, done.
    Resolving deltas: 100% (273/273), done.
    user@sputnik:~$ cd fskintra/
    user@sputnik:~/fskintra$   # ./fskintra.py ligger nu her

I det nedenstående går vi ud fra at ```fskintra```er installeret i ```~/fskintra```. Du kan naturligvis lægge programmet et andet sted.

## 2. Hent krævede pythonpaker ##

De tre krævede ekstra pythonpakker findes i de fleste linux distributioner, men pt ikke i versioner der er nye nok. Fx findes Mechanize pakken i Ubuntu 18.04 kun i version 0.2.x. Du kan se hvilke versioner der er krævet i filen ```requirements.txt```.

Den bedste løsning er derfor at bruge Python PIP, hvor selve pip nok findes
i dit Linux/Mac pakkesystem. Ellers kan du hente [PIP her](https://pypi.org/project/pip/).

    # Check først at det er pip til Python 2.x du bruger,
    # muligvis hedder programmet pip2 eller lignende:
    user@sputnik:~/fskintra$ pip -V
    pip 10.0.1 from /.../pip (python 2.7)

    user@sputnik:~/fskintra$ sudo pip install -r requirements.txt

Pakkerne kan installeres i dit hjemmekatalog, så de ikke forstyrer de pythonpakker der er installeret via dit rigtige pakkesystem (apt/npm/yum/port/osv):

    user@sputnik:~/fskintra$ pip install --user -r requirements.txt

## 3. Sæt fskintra op ##

Kør følgende kommando, og besvar spørgsmålene

    user@sputnik:~/fskintra$ ./fskintra.py --config

Ved den første rigtige kørsel kan det være en fordel at køre med ```--catchup```: I så fald hentes og markeres alt indhold som set uden faktisk at sende nogen e-mails; uden ```--catchup```får du måske mere end 100 emails per barn, da alt indhold på ForældreIntra er nyt:

    user@sputnik:~/fskintra$ ./fskintra.py --catchup

Fremadrettet køres uden parametre, alternativt med ```--quick```:

    user@sputnik:~/fskintra$ ./fskintra.py
    # eller
    user@sputnik:~/fskintra$ ./fskintra.py --quick

Din opsætning gemmes i ```~/.skoleintra/skoleintra.txt```. Såfremt du
kun skal rette lidt, er det oftest smartest at rette direkte i filen i stedet for at køre --config igen.

I ```~/.skoleintra/``` gemmes også alt hentet indhold og alle sendte
emails.

## 4. Automatisk kørsel ##

Se siden om [automatisk kørsel/cron jobs](cron) for detaljer om hvordan du sætter dette op.


## Eksempler på konfigurationsfiler ##

### En bruger på en skole ###
Helt almindelig konfigurationfil oprettet via ```--config```:

```
[default]
logintype=alm
username=peter42
password=pswd:a2FUVHgyNA==
hostname=aaskolen.m.skoleintra.dk
email=example@example.net
senderemail=example@example.net
smtpserver=smtp.gmail.com
smtpport=587
smtplogin=example@gmail.com
smtppassword=pswd:a2FUVHgyNA==
```

### To brugere på samme skole ###

Hvis man har to brugere på *samme* skole (fx mor og far) kan man lave underprofiler:

```
[default]
hostname=aaskolen.m.skoleintra.dk
email=example@example.net
senderemail=example@example.net
smtpserver=smtp.gmail.com
smtpport=587
smtplogin=example@gmail.com
smtppassword=pswd:a2FUVHgyNA==

[peter]
logintype=uni
username=peter42
password=pswd:a2FUVHgyNA==

[ida]
logintype=uni
username=ida42
password=pswd:a2FUVHgyNA==
```

Beskeder sendt til begge forældre vil dernæst kun blive udsendt én gang. Bemærk at man i så fald skal køre ```fskintra``` 2 gange: en gang med ```--profile peter``` og en gang med ```--profile ida```.

### To brugere på hver sin skole ###

NB: Hvis man har børn på flere skoler bør man sikre at hver skole har sit eget ```cacheprefix``` da man ellers risikerer at fx. beskeder der tilfældigvis har samme besked-id på de to skoler, kun bliver udsendt én gang:

```
[default]
email=example@example.net
senderemail=example@example.net
smtpserver=smtp.gmail.com
smtpport=587
smtplogin=example@gmail.com
smtppassword=pswd:a2FUVHgyNA==

[aaskolen]
hostname=aaskolen.m.skoleintra.dk
cacheprefix=aaskolen-
logintype=uni
username=peter42
password=pswd:a2FUVHgyNA==

[soeskolen]
hostname=soeskolen.m.skoleintra.dk
cacheprefix=soeskolen-
logintype=alm
username=peter42
password=pswd:a2Fa2FUVHgyNA==
```
