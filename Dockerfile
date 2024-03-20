FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE 'config.settings'

WORKDIR /drf_spa

COPY ./requirements.txt /drf_spa/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
