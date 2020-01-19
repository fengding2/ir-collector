FROM balenalib/generic-armv7ahf-alpine-python:3.7.6-edge

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim

RUN pip install -U pip && \
    pip install --user pipenv

RUN mkdir -p /root/workspace
RUN cd /root/workspace/  && git clone https://deathkingdomking:4021450247a66014b51c8f8f7dd26d3552bf4817@github.com/WeConnect/cn-eventcollector-python 
RUN cd /root/workspace/cn-eventcollector-python && python3 setup.py install

WORKDIR /root/workspace
COPY . .
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r /root/workspace/requirements.txt


EXPOSE 5000
ENV FLASK_APP=/root/workspace/src/app.py