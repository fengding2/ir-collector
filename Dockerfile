FROM balenalib/generic-armv7ahf-alpine-python:3.7.6-edge

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git vim

RUN pip install -U pip && \
    pip install --user pipenv



WORKDIR /usr/src/app

COPY . .

EXPOSE 5000
ENV FLASK_APP=src/app.py

CMD [ "python", "./your-daemon-or-script.py" ]