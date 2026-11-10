FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput && chmod +x entrypoint.sh && chgrp -R 0 /app && chmod -R g=u /app
USER 1001
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "django_concert.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
