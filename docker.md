# ForældreIntra in a box

## Prerequisites

[Docker](https://www.docker.com/)

## Setup

    python fskintra.py --config
    docker-machine start
    docker build -t fintra .

## Start

### Local

    docker run -v ~/.skoleintra:/root/.skoleintra -t fintra

### Server

    cp -R ~/.skoleintra/* .skoleintra
    docker run -v $(pwd)/.skoleintra:/root/.skoleintra -t fintra

## PanicButton

Stop all docker containers:

    docker stop $(docker ps -a -q)
