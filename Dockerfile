FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

WORKDIR /vkbot

COPY . .

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

CMD ["python", "-u", "poller.py"]
CMD ["python", "-u", "worker.py"]
CMD ["python", "-u", "sender.py"]

