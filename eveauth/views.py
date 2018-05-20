from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings

from . import models
from . import simple_sso


EVEAUTH_SCOPES = [
    'esi-wallet.read_character_wallet.v1',
    'esi-skills.read_skillqueue.v1',
    'esi-skills.read_skills.v1',
]


def index(request):
    return HttpResponse("auth index page")


@login_required
def character_list(request):
    characters = models.AccessToken.objects.filter(user=request.user)
    return render(request, 'eveauth/character_list.html', context={
        'characters': characters,
    })


@login_required
def character_add(request):
    auth_request = models.AuthenticationRequest(user=request.user)
    auth_request.save()

    sso_link = simple_sso.login_link(request.build_absolute_uri(reverse('eveauth:sso_callback')),
                                     settings.EVESSO_CLIENT_ID,
                                     EVEAUTH_SCOPES,
                                     auth_request.key)
    return redirect(sso_link)


@login_required
def character_delete(request, token_id):
    token = models.AccessToken.objects.get(pk=token_id)
    if request.user != token.user:
        return HttpResponseForbidden()

    token.delete()
    return redirect(reverse('eveauth:char_list'))


def sso_callback(request):
    request_key = request.GET.get('state')
    authentication_code = request.GET.get('code')

    auth_request = models.AuthenticationRequest.objects.get(key=request_key)
    user = auth_request.user

    models.AccessToken.from_oauth(user, authentication_code)

    auth_request.delete()

    return redirect(reverse('eveauth:char_list'))
