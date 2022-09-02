# Docker opsætning / Installation #

fskintra kan også køres i [Docker](https://www.docker.com/).

## Opsætning ##

Hent nyeste version af fskintra fra Docker Hub:

```bash
docker pull svalgaard/fskintra
```

Lav en konfigurationsfil ved at køre følgende Docker-kommando:

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra svalgaard/fskintra --config
```

Lav endvidere evt. et lille bash script der starter fskintra via Docker:

```bash
#! /bin/bash
#
# Gemmes fx i /bin/fskintra
# Kan IKKE bruges når du skal køre med --config

docker run --rm -v ~/.skoleintra:/root/.skoleintra svalgaard/fskintra "$@"
```

Bemærk at docker her *ikke* bliver kørt med `-it` parameteren og derfor ikke bliver
kørt iteraktivt (dvs. du kan *ikke* bruge det, når du vil køre fskintra med `--config`.

Selve Docker containeren bliver automatisk slettet (`--rm`) efter hver kørsel,
mens opsætningen, cache, osv bliver gemt lokalt i `~/.skoleintra`.
Du starter derfor bare en ny container hver gang du vil hente nyt.


## Kørsel ##

Nu kan du køre fskintra i Docker med følgende kommando:

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra svalgaard/fskintra
# ELLER
/bin/fskintra
```

## Cron ##

Du kan evt bruge Docker kommandoen i [cron](cron.md):

```bash
15 6,17 * * * /usr/bin/docker run --rm -v ~/.skoleintra:/root/.skoleintra svalgaard/fskintra
ELLER
15 6,17 * * * /bin/fskintra
```

Bemærk at `-it` *ikke* skal med, da det ikke er en interaktiv kørsel.


## Opdatering ##

Hvis der kommer ny udgave af fskintra, hentes et nyt med `docker pull`:

```
docker pull svalgaard/fskintra
```

## Docker med egne ændringer ##

I stedet for at bruge det officielle `svalgaard/fskintra` Docker image,
kan du bygge dit eget i samme katalog som `Dockerfile` filen ligger i:

```bash
docker build -t fskintra .
```

Hvis du har ændret filer selv / har hentet opdateringer med git,
bygges et nyt image ved først at slette det gamle og lave et nyt:

```bash
docker image rm  -f fskintra
docker build -t fskintra .
```

Se i øvrigt [opgraderingsvejledningen](upgrade.md).
