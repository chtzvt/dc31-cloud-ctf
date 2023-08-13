FROM python:3.9-slim

RUN apt-get clean && apt-get -y update

RUN apt-get -y install python3-dev build-essential

WORKDIR /app

COPY ./Flask-CTF-Cloud/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./Flask-CTF-Cloud /app/

CMD [ "python", "app.py" ]
