FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY ../../requirements.txt .

RUN pip install --user -r requirements.txt

WORKDIR /poller/

COPY ../.. .

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

