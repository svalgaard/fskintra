# Automatisk jobkørsel - cron jobs

Efter at du har fået fskintra til at virke fint ved at køre det manuelt et par gange, vil de fleste gerne køre programmet nogle gange om dagen. Hvordan du gør det, afhænger af hvilken type computer du kører på.

## Linux

De fleste Linux computere har et system til at køre jobs automatisk kaldet cron. For at rette i din cron-fil, køres ```crontab -e```:

    user@sputnik:~$ crontab -e

Du kan tilføje følgende linje til din crontab fil for at få programmet til at køre
fire gange dagligt - kl. 6:25, 7:25, 11:25 og 20:25:

    PYTHONIOENCODING=UTF-8
    25 6,7,11,20 * * * /path/to/fskintra.py -q --quick

Ved at tilføje -q, får du kun en email, såfremt der er noget interessant at se (og ikke en email om, at fskintra har prøvet at finde noget nyt uden at gøre det).

Linjen med PYTHONIOENCODING=UTF-8 er ikke altid nødvendig (se [evt denne side](troubleshooting))
men er næsten altid en god idé.

## Mac

De fleste versioner af Mac OS X har cron installeret. Hvis din mac har, er det nemmeste at bruge cron. Se under Linux.

Alternativt kan man bruge ```launchd```.

Kopier launchd-filen over:

    user@sputnik:~/fskintra cp _services/Mac/com.github.fskintra.plist ~/Library/LaunchAgents/

Ret inde i filen til så stien til run-cron.sh (se nedenfor) passer:

    user@sputnik:~/fskintra$ nano ~/Library/LaunchAgents/com.github.fskintra.plist

Sæt launchd til at køre scriptet:

    user@sputnik:~/fskintra$ launchctl load -w ~/Library/LaunchAgents/com.github.fskintra.plist

Stop launchd i at køre scriptet

    user@sputnik:~/fskintra$ launchctl unload -w ~/Library/LaunchAgents/com.github.fskintra.plist

Husk at tjekke indholdet i ```/tmp/fskintra.log``` og ```/tmp/fskintra-error.log```.
