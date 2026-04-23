FROM python:3.11-slim

# dossier travail
WORKDIR /app

# dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/*

# dépendances Python
COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code application
COPY webapp/ /app/webapp/

# variable environnement
ENV PYTHONPATH=/app

# port
EXPOSE 5000

# healthcheck container (important EC2)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# lancement
CMD ["python", "webapp/app.py"]