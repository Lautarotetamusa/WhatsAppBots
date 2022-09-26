FROM python:3.10.7-alpine3.16
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
