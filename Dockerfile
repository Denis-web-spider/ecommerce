FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /ecommerce

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv && pipenv install --system
