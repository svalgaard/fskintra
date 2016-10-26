# ForældreIntra in a box

## Prerequisites

[Docker](https://www.docker.com/)

## Setup

    python fskintra.py --config
    docker-machine start
    docker build -t fintra .

## Start

    docker run -v ~/.skoleintra:/root/.skoleintra -t fintra

## PanicButton

Stop all docker containers:

    docker stop $(docker ps -a -q)
