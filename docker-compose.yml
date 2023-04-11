FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install requirements.txt

ENV PATH=/root/.local:$PATH

CMD ["python", "./poller.py"]

