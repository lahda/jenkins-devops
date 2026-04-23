# ──────────────────────────────────────────────
# Stage 1 : build & test
# ──────────────────────────────────────────────
FROM python:3.11-alpine AS builder

WORKDIR /app

# Dépendances système minimales
RUN apk add --no-cache gcc musl-dev

# Installer les dépendances Python
COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY webapp/ ./webapp/
COPY tests/ ./tests/

# ──────────────────────────────────────────────
# Stage 2 : image de production
# ──────────────────────────────────────────────
FROM python:3.11-alpine AS production

WORKDIR /opt/app

# Créer un utilisateur non-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Installer uniquement gunicorn + flask
COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier uniquement le code de l'application
COPY webapp/ .

# Donner les droits à l'utilisateur
RUN chown -R appuser:appgroup /opt/app
USER appuser

# Variables d'environnement par défaut
ENV PORT=5000
ENV APP_VERSION=1.0.0
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:${PORT}/health || exit 1

CMD gunicorn --bind 0.0.0.0:${PORT} --workers=2 --timeout=60 wsgi:app
