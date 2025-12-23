FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app
COPY compareproduct /app

Run apt-get update && \
    pip install -r requirements.txt && \
    cd compareproduct


CMD ["python","manage.py","runserver","0.0.0.0:8000"]