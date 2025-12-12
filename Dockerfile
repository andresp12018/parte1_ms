FROM python:3.11-slim

# Evitar buffers en stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos primero requirements para aprovechar cache de docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la app
COPY app ./app

# Puerto expuesto por uvicorn
EXPOSE 8000

# Comando por defecto para ejecutar la app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
