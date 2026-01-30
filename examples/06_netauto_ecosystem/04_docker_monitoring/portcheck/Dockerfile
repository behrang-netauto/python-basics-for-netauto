
FROM python:3.12-slim

RUN apt update \
 && apt install -y --no-install-recommends iputils-ping \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY portcheck.py /app/portcheck.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/portcheck.py"]