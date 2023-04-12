FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN pip install --user -r requirements.txt

ADD .. /worker/

WORKDIR /worker/

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

