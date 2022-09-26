FROM python:3.10.7-alpine3.16
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apk update
RUN apk add chromium chromium-chromedriver xvfb

COPY app/start_xvfb.sh .
RUN chmod +x ./start_xvfb.sh
