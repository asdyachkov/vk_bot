FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD app /sender/app
ADD sender.py /sender/
ADD VERSION /sender/
ADD config.yaml /sender/

WORKDIR /sender/

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

