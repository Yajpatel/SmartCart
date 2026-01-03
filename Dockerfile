FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first (layer caching)
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY compareproduct /app/compareproduct

EXPOSE 8000

CMD ["python", "compareproduct/manage.py", "runserver", "0.0.0.0:8000"]
