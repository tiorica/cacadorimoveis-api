# Caçador Imóveis API
## API for cacadorimoveis-suite.

Developed using [Flask](https://flask.palletsprojects.com/)

## Message broker
## Runs the service using docker
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
## Install pika library
python -m pip install pika --upgrade