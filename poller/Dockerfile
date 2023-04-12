FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN pip install --user -r requirements.txt

WORKDIR /vkbot/

ADD .. /vkbot/

EXPOSE 8000
EXPOSE 5672
EXPOSE 15672

