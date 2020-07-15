FROM python:2.7

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app
COPY . /app/service
COPY . /app/templates
COPY . /app/static

ENTRYPOINT [ "python" ]

CMD [ "main.py", "-h", "0.0.0.0", "p", "5000" ]