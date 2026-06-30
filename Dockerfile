FROM python:3.10-slim

WORKDIR /app

COPY . .

# Comando padrão
CMD ["python", "mechape_hub.py"]