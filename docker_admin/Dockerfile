FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD . /docker_admin/

WORKDIR /docker_admin/

EXPOSE 8000
