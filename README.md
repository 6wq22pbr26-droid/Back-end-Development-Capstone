# Djirection band website — Backend Development Capstone

Django application integrating the Pictures and Songs Flask microservices, based on the IBM Developer Skills Network template. Prepared by Sabina Zhumagaliyeva with AI coding assistance. Original template attribution is retained. The band, tour, attendance records, and accounts are educational demo data.

## Local setup

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Run the Pictures service on port 8801 and Songs on 8802, or set `PICTURES_SERVICE_URL` and `SONGS_SERVICE_URL`. Pages include Home, Songs with a lyrics modal, Photos, registration, login/logout, authenticated concert attendance, and Django administration.

## Container and Kubernetes

```sh
docker build -t band-website .
# Configure a real secret key, allowed hosts, service URLs, and optional demo admin via environment.
docker run --rm --env-file .env -p 8000:8000 band-website
# Create the band-config Kubernetes secret from your private environment file first.
# Set DJANGO_IMAGE to your pushed registry image.
envsubst < deployment.yml | kubectl apply -f -
kubectl port-forward svc/djangoserver 8080:8080
```

Secrets are intentionally absent from this repository. `DJANGO_DEBUG=0` is required outside local development. Set `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, and `DJANGO_SECRET_KEY` explicitly. Startup applies existing migrations and idempotently creates fictional demo concerts; an admin is created only if `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` are provided. Static assets are served by WhiteNoise.

The educational container uses SQLite and one replica. Container replacement loses unmounted data. Use a persistent database, backups, TLS, and appropriate operational controls for any production adaptation. Local checks confirm HTTP pages, real microservice reads, and authenticated concert access. A successful local check alone does not claim a cloud deployment.
