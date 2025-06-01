# Etap 1: Budowanie
FROM python:3.12-slim AS builder

LABEL maintainer="Kateryna Zinchuk"

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY main.py .

# Etap 2: Finalny obraz
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY main.py .

ENV PATH=/root/.local/bin:$PATH
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
