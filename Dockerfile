FROM python:3.12-slim

WORKDIR /app/

COPY requirements.txt /app/
COPY compareproduct /app/

RUN apt-get update && \
    pip install -r requirements.txt


CMD ["python","manage.py","runserver","0.0.0.0:8000"]
