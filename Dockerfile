FROM python:3.12-slim AS builder
# FROM "mcr.microsoft.com/devcontainers/python:1-3.12-bullseye"

WORKDIR /workspace/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

WORKDIR /workspace/app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

CMD streamlit run app/main.py