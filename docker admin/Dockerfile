FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --user -r requirements.txt

ADD vk_bot_admin /vk_bot_admin/

WORKDIR /vk_bot_admin/

EXPOSE 8000
