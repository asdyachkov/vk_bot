FROM python:3.10

ENV PYTHONUNBUFFERED 1

ADD .. /worker/

WORKDIR /worker/

RUN pip install --user -r requirements.txt

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

