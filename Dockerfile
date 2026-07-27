FROM python:3.11-slim

WORKDIR /app

COPY uptime.py .

RUN pip install --no-cache-dir requests

EXPOSE 10000

CMD ["python", "uptime.py"]
