FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt

ENV PATH=/root/.local:$PATH

CMD ["python", "./poller.py"]
CMD ["python", "./worker.py"]
CMD ["python", "./sender.py"]

