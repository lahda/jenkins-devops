# DevOps Task Manager 🚀

Application Flask containerisée avec pipeline CI/CD Jenkins complet.

## Structure du projet

```
devops-project/
├── Dockerfile              # Image multi-stage (build + production)
├── Jenkinsfile             # Pipeline CI/CD complet (6 stages)
├── docker-compose.yml      # Dev local
├── webapp/
│   ├── app.py              # Application Flask
│   ├── wsgi.py             # Entry point Gunicorn
│   ├── requirements.txt    # Dépendances Python
│   └── templates/
│       └── index.html      # Interface web
└── tests/
    └── test_app.py         # Tests unitaires (pytest)
```

## Lancer en local

```bash
# Avec Docker Compose
docker-compose up -d

# Sans Docker
cd webapp && pip install -r requirements.txt
PORT=5000 python app.py
```

## Pipeline Jenkins — 6 étapes

| Stage | Description |
|---|---|
| 📥 Checkout | Clone du dépôt Git |
| 🧪 Unit Tests | Tests pytest |
| 🔨 Build | Construction de l'image Docker |
| ✅ Acceptance | Tests sur container live |
| 🚀 Push | Push vers Docker Hub |
| 🌍 Deploy | Déploiement en production |

## Configuration Jenkins requise

1. **Credentials** : ajouter `dockerhub-credentials` (username/password Docker Hub)
2. **Modifier** `DOCKER_USER` dans le Jenkinsfile avec votre username Docker Hub
3. **Pipeline** : New Item → Pipeline → Pipeline script from SCM → Git

## Endpoints API

| Méthode | URL | Description |
|---|---|---|
| GET | `/` | Interface web |
| GET | `/health` | Healthcheck |
| GET | `/api/tasks` | Liste des tâches |
| POST | `/api/tasks` | Créer une tâche |
| DELETE | `/api/tasks/:id` | Supprimer une tâche |
