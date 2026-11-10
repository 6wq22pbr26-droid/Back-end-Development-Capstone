import os
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from concert.models import Concert

class Command(BaseCommand):
    help = "Idempotently seed fictional demonstration concerts; optionally create an admin from environment."
    def handle(self, *args, **options):
        for day, city in [(5, "Astana"), (12, "Almaty"), (19, "London")]:
            Concert.objects.get_or_create(name="Djirection — Demo Tour", city=city, date=date(2026, 12, day), defaults={"duration": 120})
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if username and password and not get_user_model().objects.filter(username=username).exists():
            get_user_model().objects.create_superuser(username, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), password)
        self.stdout.write("Fictional demonstration concerts are ready.")
