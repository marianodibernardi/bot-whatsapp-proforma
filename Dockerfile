FROM python:3.11-bullseye


# ✅ Establecer carpeta de trabajo
WORKDIR /app

# ✅ Instalar librerías necesarias para pyodbc, SQL Server y ngrok
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    gcc \
    g++ \
    gnupg \
    unixodbc-dev \
    libodbc1 \
    libpq-dev \
    apt-transport-https \
    software-properties-common \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copiar primero requirements.txt para aprovechar cache
COPY requirements.txt ./

# ✅ Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copiar el resto del proyecto
COPY . .

# ✅ Instalar ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok && \
    rm -rf /var/lib/apt/lists/*

# ✅ Preparar script de inicio
RUN chmod +x /app/entrypoint.sh

# ✅ Exponer puertos necesarios
EXPOSE 5000 4040

# ✅ Variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_ENV=production

# ✅ Comando de inicio
CMD ["/app/entrypoint.sh"]
