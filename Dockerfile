FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

WORKDIR /vk_bot

COPY ./app .
COPY ./vk_bot_admin .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "poller.py"]
CMD ["python", "-u", "worker.py"]
CMD ["python", "-u", "sender.py"]

