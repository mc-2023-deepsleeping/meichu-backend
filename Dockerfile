FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive TZ="Asia/Taipei"
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install python 3.10
RUN apt-get update -y && apt-get upgrade --no-install-recommends -y
# RUN apt-get install build-essential -y

# Install pip
# RUN apt-get install curl -y
# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# RUN python3.10 get-pip.py

# set work directory
RUN mkdir -p /opt/app
COPY . /opt/app
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel 
RUN pip install -r /opt/app/requirements.txt

EXPOSE 5000

RUN chmod +x /opt/app/docker-entrypoint.sh
ENTRYPOINT [ "/opt/app/docker-entrypoint.sh" ]