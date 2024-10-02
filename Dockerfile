FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el directorio actual al contenedor en /app
COPY . .

COPY requirements.txt requirements.txt

# Instalar requisitos
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de entrada
COPY entrypoint.sh .

# Establece el script como el comando de inicio
CMD ["./entrypoint.sh"]