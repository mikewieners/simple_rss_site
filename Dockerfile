FROM python:3.7-slim

EXPOSE 8000

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

ADD . /

WORKDIR /

RUN pip install -r requirements.txt

RUN python manage.py makemigrations

RUN python manage.py migrate

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]