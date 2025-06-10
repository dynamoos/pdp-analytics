# Usar imagen base de Python 3.11 slim
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt* pyproject.toml* ./

# Instalar dependencias
RUN pip install -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs output templates

# Exponer puerto
EXPOSE 9004

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "src.adapters.input_adapters.api.main:app", "--host", "0.0.0.0", "--port", "9004"]