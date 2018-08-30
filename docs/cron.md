# Automatisk jobkørsel - cron jobs

Efter at du har fået fskintra til at virke fint ved at køre det manuelt et par
gange, vil de fleste gerne køre programmet automatisk nogle gange om dagen.
Hvordan du gør det, afhænger af hvilken type computer du kører på.

## Script-fil

For at sikre dig, at du får kørt fskintra med de parametre du gerne vil,
kan det være en god idé at lave en lille script-fil, der gør det hele rigtigt.
Du kan tage udgangspunkt i filen ```docs/assets/run-cron-example.sh```, som
bør kopiere til samme sted som selve ```fskintra.py```og dernæst rette til.
Indhold kunne se sådan her ud:

```bash
#! /bin/bash
#
# Kopier nedenstående fil ned i samme katalog som fskintra.py og ret den
# til. Dette er smart til fx. cronjobs såfremt du har brug for en særlig
# version af python m.v.
#

# Sikr at Python kan finde ud af at lave UTF-8
export PYTHONIOENCODING=UTF-8

# Gå til samme bibliotek som denne fil ligger i
ROOT="$(dirname "$0")"
cd "$ROOT"

# Kør fskintra som default bruger
python ./fskintra.py --quiet --quick

# Kør fskintra som en anden bruger
# python ./fskintra.py --quiet --quick --profile ida
```

Linjen med ```PYTHONIOENCODING=UTF-8``` er ikke altid nødvendig
(se [evt denne side](troubleshooting.md)) men er næsten altid en god idé ift at
Python ellers nemt kan give problemer med danske bogstaver.

Ved at tilføje ```--quiet``` skriver ```fskintra``` kun noget ud, hvis der er
noget der går galt.

Ved at tilføje ```--quick``` laver ```fskintra``` et dagligt grundigt tjek
for nyt ved første kørsel om morgenen.
Senere på dagen laves kun et grundigt kørsel, såfremt det ligner,
at der er sket noget nyt på hjemmesiden


## Linux

De fleste Linux computere har et system til at køre jobs automatisk kaldet
cron. For at rette i din cron-fil, køres ```crontab -e```:

```console
user@sputnik:~$ crontab -e
```

Du kan tilføje følgende linjer til din crontab fil for at få programmet til at
køre fire gange dagligt - kl. 6:25, 7:25, 11:25 og 20:25:

```
25 6,7,11,20 * * * /sti/til/run-cron.sh
```

## Mac

De fleste versioner af Mac OS X har cron installeret. Hvis din mac har, er det
nemmest at bruge cron. Se under afsnittet om linux ovenover.

Alternativt kan man bruge ```launchd```.

Kopier launchd-filen over:

```console
user@sputnik:~/fskintra cp docs/assets/com.github.fskintra.plist ~/Library/LaunchAgents/
```

Ret inde i filen til så stien til ```run-cron.sh``` (se ovenover) passer:

```console
user@sputnik:~/fskintra$ nano ~/Library/LaunchAgents/com.github.fskintra.plist
```

Sæt launchd til at køre scriptet:

```console
user@sputnik:~/fskintra$ launchctl load -w ~/Library/LaunchAgents/com.github.fskintra.plist
```

På et evt. senere tidspunkt: Stop launchd i at køre scriptet

```console
user@sputnik:~/fskintra$ launchctl unload -w ~/Library/LaunchAgents/com.github.fskintra.plist
```

Husk at tjekke indholdet i ```/tmp/fskintra.log``` og ```/tmp/fskintra-error.log```.
