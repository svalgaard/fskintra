# fskintra i Docker

[Docker](https://www.docker.com/)

Hvis du bruger Docker, kan dette også forholdsvist nemt sættes op.

    docker build -t fskintra .

Dernæst konfigurerer og kører du fskintra ligesom du plejer bortset fra at du
bruger `docker-run.sh` i stedet for `fskintra.py`, fx.

    docker-run.sh --config

Eller blot

    docker-run.sh --config

Data m.v. gemmes stadigvæk i `~/.skoleintra`.

## Panik?

Stop alle docker containere, hvis noget går galt:

    docker stop $(docker ps -a -q)
