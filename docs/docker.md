# Docker Opsætning / Installation # 

fskintra kan også køres i docker

Byg et image med følgende kommando:

```bash
docker build -t fskintra .
```

Lav en konfig, enten som beskrevet i [Installationsvejledningen](install) 
eller ved at køre følgende docker kommando :

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra fskintra --config
```

Nu kan du køre fskintra i docker med følgende kommando:

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra fskintra 
```
Docker containeren bliver automatisk slettet (`--rm`) efter hverkørsel, men din 
opæstning cache osv ligger stadig lokalt i `~/.skoleintra`, så du starter bare
en ny container hver gang du vil hente nyt.

Du kan evt sætte docker kommandoen i [cron](cron):

```bash
15 6,17 * * * /usr/bin/docker run --rm -v ~/.skoleintra:/root/.skoleintra fskintra
```
