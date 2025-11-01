FROM python:3.11-slim

RUN groupadd -r appuser && useradd -m -r -g appuser appuser

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app

EXPOSE 8080

USER appuser

ENV FLASK_APP=main.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app", "--workers", "2", "--threads", "4", "--timeout", "120"]
