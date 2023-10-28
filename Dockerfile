FROM python:3.11

ADD . /code
WORKDIR /code

RUN pip3 install poetry
RUN poetry install
