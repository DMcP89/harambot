FROM python:3.8.10-slim

WORKDIR /app/harambot

ADD . /app/harambot

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc libc-dev make git libffi-dev python3-dev libxml2-dev libxslt-dev 

RUN pip install -U pip

RUN pip install -r requirements.txt

CMD ["make", "run"]
