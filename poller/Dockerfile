FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD app /poller/app
ADD poller.py /poller/
ADD VERSION /poller/
ADD config.yaml /poller/

WORKDIR /poller/

CMD ["python", "./poller.py"]

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

