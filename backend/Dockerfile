FROM python:3.11-slim
# Définir le répertoire de travail dans le conteneur
WORKDIR /app
# Make Python able to import the "app" package
ENV PYTHONPATH=/app
# Copier le fichier des dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copier tout le code de l'application
COPY . .
# Exposer le port utilisé par FastAPI
EXPOSE 8000
# Lancer l'application FastAPI via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
