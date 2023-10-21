FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt