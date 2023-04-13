FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD . /admin/

WORKDIR /admin/

EXPOSE 8000
