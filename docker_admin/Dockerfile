FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD . /vk_bot_admin/

WORKDIR /vk_bot_admin/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
