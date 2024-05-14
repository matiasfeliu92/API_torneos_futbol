# Utilizamos una imagen base de Python
FROM python:3.9

# Establecemos el directorio de trabajo en /app
WORKDIR /app

# Copiamos el archivo de requisitos al contenedor
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install -r requirements.txt

# Copiamos todos los archivos de la aplicación al contenedor
COPY . .

# Exponemos el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]