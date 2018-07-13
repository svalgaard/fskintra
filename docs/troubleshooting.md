# Problemer? #

## UnicodeEncodeError ##
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
```PYTHONIOENCODING``` til UTF-8.

Hvis du bruger bash eller lignende (hvis du ikke ved, om du gør, så gør
du sikkert).

    export PYTHONIOENCODING=UTF-8
    /sti/til/fskintra

Hvis du bruger tcsh eller lignende:

    setenv PYTHONIOENCODING UTF-8
    /sti/til/fskintra

## HTTP/HTML fejl ##
Den nuværende version af fskintra er ikke altid god til at håndtere
http/html fejl. Hvis der sker en fejl, kan du for det meste løse
problemet ved at køre fskintra igen. Hvis det ikke er nok, kan du
evt. tilføje parameteren -v for muligvis at se mere om, hvad der går
galt:

    fskintra.py -v

Du er evt. også velkommen til at lave et ["issue"](https://github.com/svalgaard/fskintra/issues) på Github. Såfremt det ikke
virker, er det meget smart at vedhæfte / kopiere teksten af fra en kørsel med ```fskintra -v -v```.
