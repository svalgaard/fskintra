# Problemer? #

## Python 2 ? ##

Hvis man prøver at køre ```fskintra``` med Python version 3.x -
fx. hvis ens standard Python version netop er version 3 -
får man en fejl lignende følgende:

```python
user@sputnik:~/fskintra$ ./fskintra.py
fskintra kræver Python version 2.7.x
Python version 3.7.2 er installeret
Se evt. her for hjælp:
    https://svalgaard.github.io/fskintra/install#krav
```

Løsningen er først at sikre at man har Python 2.7.x installeret og dernæst
eksplicit vælge den når man kører ```fskintra```, fx:

```console
user@sputnik:~/fskintra$ python2 ./fskintra.py
```


## UnicodeEncodeError ##

I nogle situationer giver Python desværre en unicode-fejl lignende følgende

```python
Traceback (most recent call last):
  File "/Users/user/fskintra/fskintra.py", line 12, in <module>
    cnames = skoleintra.schildren.skoleGetChildren()
  File "/Users/user/fskintra/skoleintra/schildren.py", line 22, in skoleGetChildren
    config.log(u'Henter liste af bM-CM-8rn')
  File "/Users/user/fskintra/skoleintra/config.py", line 185, in log
    sys.stderr.write(u'%s\n' % s)
UnicodeEncodeError: 'ascii' codec can't encode character u'\xf8' in position 17: ordinal not in range(128)
```

En løsning vil i næsten alle tilfælde være at sætte
miljøvariablen ```PYTHONIOENCODING``` til ```UTF-8```.

Hvis du bruger bash eller lignende (hvis du ikke ved, om du gør, så gør
du sikkert):

```console
user@sputnik:~/fskintra$ export PYTHONIOENCODING=UTF-8
user@sputnik:~/fskintra$ /sti/til/fskintra.py
```

Hvis du bruger tcsh eller lignende:

```console
user@sputnik:~/fskintra$ setenv PYTHONIOENCODING UTF-8
user@sputnik:~/fskintra$ /sti/til/fskintra.py
```

## HTTP/HTML fejl ##

Den nuværende version af fskintra er ikke altid god til at håndtere
http/html fejl.
Hvis der sker en fejl, kan du for det meste løse problemet ved at køre
fskintra igen lidt senere.
Hvis det ikke er nok, kan du evt. tilføje parameteren ```-v``` for
muligvis at se mere om, hvad der går galt:

```console
fskintra.py -v
```

Du er evt. også velkommen til at lave et
["issue"](https://github.com/svalgaard/fskintra/issues) på Github.
Det er ofte meget smart at vedhæfte / kopiere den *relevante del* af
teksten fra en kørsel med ```fskintra.py -v -v``` så er det lettere at se,
hvad der er galt - fjern i så fald altid navne på børn osv.
