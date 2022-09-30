FROM python:3.10.7-slim

WORKDIR /app/harambot

ADD ./Makefile /app/harambot
ADD ./requirements.txt /app/harambot/
ADD ./harambot /app/harambot/harambot
ADD ./config /app/harambot/config

RUN apt-get update
RUN apt-get upgrade -y 
RUN apt-get install -y gcc libc-dev make git libffi-dev python3-dev libxml2-dev libxslt-dev

RUN apt-get install -y default-libmysqlclient-dev

RUN apt-get install -y libpq-dev

RUN pip install -U pip

RUN pip install -r requirements.txt

RUN ls -ltr /app/harambot

CMD ["python", "./harambot/bot.py"]
