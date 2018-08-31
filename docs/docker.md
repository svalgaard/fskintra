# Docker opsætning / Installation #

fskintra kan også køres i [Docker](https://www.docker.com/).

## Opsætning ##

Byg et Docker image med følgende kommando:

```bash
docker build -t fskintra .
```

Lav en konfiguration, enten som beskrevet i [installationsvejledningen](install.md)
eller ved at køre følgende Docker kommando :

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra fskintra --config
```

## Kørsel ##

Nu kan du køre fskintra i Docker med følgende kommando:

```bash
docker run --rm -it -v ~/.skoleintra:/root/.skoleintra fskintra
```

Selve Docker containeren bliver automatisk slettet (`--rm`) efter hver kørsel,
mens opsætningen, cache, osv bliver gemt lokalt i `~/.skoleintra`.
Du starter derfor bare en ny container hver gang du vil hente nyt.


## Cron ##

Du kan evt bruge Docker kommandoen i [cron](cron.md):

```bash
15 6,17 * * * /usr/bin/docker run --rm -v ~/.skoleintra:/root/.skoleintra fskintra
```

Bemærk at `-it` ikke skal med, da det ikke er en interaktiv kørsel.


## Opdatering ##

Hvis der kommer ny udgave af fskintra, skal Docker image'et bygges forfra.
Dette gøres lettest ved at fjerne det gamle image og lave et nyt.

```bash
docker image rm  -f fskintra
docker build -t fskintra .
```

Se i øvrigt [opgraderingsvejledningen](upgrade.md).
