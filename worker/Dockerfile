FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD app /worker/app
ADD worker.py /worker/
ADD VERSION /worker/
ADD config.yaml /worker/

WORKDIR /worker/

CMD ["python", "./worker.py"]

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

