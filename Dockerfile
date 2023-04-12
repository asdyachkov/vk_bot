FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

WORKDIR /vkbot

COPY . .

CMD ["python", "-u", "poller.py"]
CMD ["python", "-u", "worker.py"]
CMD ["python", "-u", "sender.py"]

