from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            validate_password(form.cleaned_data['password'])
            user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except (IntegrityError, ValidationError):
            form.add_error(None, 'Choose a unique username and a valid password.')
    return render(request, 'signup.html', {'form': form})


def index(request):
    return render(request, "index.html")


def songs(request):
    try:
        response = req.get(settings.SONGS_SERVICE_URL + '/song', timeout=5)
        response.raise_for_status()
        data = response.json()['songs']
    except (req.RequestException, ValueError, KeyError):
        return render(request, 'songs.html', {'songs': [], 'service_error': 'The songs service is temporarily unavailable.'}, status=503)
    return render(request, 'songs.html', {'songs': data})


def photos(request):
    try:
        response = req.get(settings.PICTURES_SERVICE_URL + '/picture', timeout=5)
        response.raise_for_status()
        data = response.json()
    except (req.RequestException, ValueError):
        return render(request, 'photos.html', {'photos': [], 'service_error': 'The pictures service is temporarily unavailable.'}, status=503)
    photo_id = request.GET.get('id')
    if photo_id is not None:
        try:
            data = [photo for photo in data if photo['id'] == int(photo_id)]
        except ValueError:
            raise Http404('Invalid photo identifier')
        if not data:
            raise Http404('Photo not found')
    return render(request, 'photos.html', {'photos': data, 'single_photo': photo_id is not None})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def concerts(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    items = []
    for concert in Concert.objects.all().order_by('date'):
        attending = concert.attendee.filter(user=request.user).first()
        items.append({'concert': concert, 'status': attending.attending if attending else '-'})
    return render(request, 'concerts.html', {'concerts': items})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = get_object_or_404(Concert, pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
