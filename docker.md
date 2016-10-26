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

#### Mac

Adjust line 9, then:

    cp _services/Mac/dk.webcom.fintra.plist ~/Library/LaunchAgents
    launchctl load -w ~/Library/LaunchAgents/dk.webcom.fintra.plist

## PanicButton

Stop all docker containers:

    docker stop $(docker ps -a -q)
