FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el directorio actual al contenedor en /app
COPY . .

# Instalar requisitos
RUN pip install --no-cache-dir -r requirements.txt

# Establece el script como el comando de inicio
CMD ["./entrypoint.sh"]