FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends

# RUN mkdir -p /opt/app
WORKDIR /opt/app

COPY . /opt/app
RUN pip install --upgrade pip
RUN pip install -r /opt/app/requirements.txt
