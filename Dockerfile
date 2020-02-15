FROM python:3.7.4

WORKDIR /app

ADD . /app

RUN pip install -trusted-host pypi.python.org -r requirements.txt

CMD ["python", "harambot.py"]