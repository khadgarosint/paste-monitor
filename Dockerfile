FROM python:3.6-alpine3.6

RUN apk add --update libxml2 g++ gcc libxslt-dev

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python paste-monitor.py

