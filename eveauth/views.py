from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings

from . import models
from . import simple_sso


#EVEAUTH_SCOPES = [
#    'esi-wallet.read_character_wallet.v1',
#    'esi-skills.read_skillqueue.v1',
#    'esi-skills.read_skills.v1',
#]

ALL_SCOPES = ['esi-calendar.respond_calendar_events.v1', 'esi-calendar.read_calendar_events.v1', 'esi-location.read_location.v1', 'esi-location.read_ship_type.v1', 'esi-mail.organize_mail.v1', 'esi-mail.read_mail.v1', 'esi-mail.send_mail.v1', 'esi-skills.read_skills.v1', 'esi-skills.read_skillqueue.v1', 'esi-wallet.read_character_wallet.v1', 'esi-wallet.read_corporation_wallet.v1', 'esi-search.search_structures.v1', 'esi-clones.read_clones.v1', 'esi-characters.read_contacts.v1', 'esi-universe.read_structures.v1', 'esi-bookmarks.read_character_bookmarks.v1', 'esi-killmails.read_killmails.v1', 'esi-corporations.read_corporation_membership.v1', 'esi-assets.read_assets.v1', 'esi-planets.manage_planets.v1', 'esi-fleets.read_fleet.v1', 'esi-fleets.write_fleet.v1', 'esi-ui.open_window.v1', 'esi-ui.write_waypoint.v1', 'esi-characters.write_contacts.v1', 'esi-fittings.read_fittings.v1', 'esi-fittings.write_fittings.v1', 'esi-markets.structure_markets.v1', 'esi-corporations.read_structures.v1', 'esi-characters.read_loyalty.v1', 'esi-characters.read_opportunities.v1', 'esi-characters.read_chat_channels.v1', 'esi-characters.read_medals.v1', 'esi-characters.read_standings.v1', 'esi-characters.read_agents_research.v1', 'esi-industry.read_character_jobs.v1', 'esi-markets.read_character_orders.v1', 'esi-characters.read_blueprints.v1', 'esi-characters.read_corporation_roles.v1', 'esi-location.read_online.v1', 'esi-contracts.read_character_contracts.v1', 'esi-clones.read_implants.v1', 'esi-characters.read_fatigue.v1', 'esi-killmails.read_corporation_killmails.v1', 'esi-corporations.track_members.v1', 'esi-wallet.read_corporation_wallets.v1', 'esi-characters.read_notifications.v1', 'esi-corporations.read_divisions.v1', 'esi-corporations.read_contacts.v1', 'esi-assets.read_corporation_assets.v1', 'esi-corporations.read_titles.v1', 'esi-corporations.read_blueprints.v1', 'esi-bookmarks.read_corporation_bookmarks.v1', 'esi-contracts.read_corporation_contracts.v1', 'esi-corporations.read_standings.v1', 'esi-corporations.read_starbases.v1', 'esi-industry.read_corporation_jobs.v1', 'esi-markets.read_corporation_orders.v1', 'esi-corporations.read_container_logs.v1', 'esi-industry.read_character_mining.v1', 'esi-industry.read_corporation_mining.v1', 'esi-planets.read_customs_offices.v1', 'esi-corporations.read_facilities.v1', 'esi-corporations.read_medals.v1', 'esi-characters.read_titles.v1', 'esi-alliances.read_contacts.v1', 'esi-characters.read_fw_stats.v1', 'esi-corporations.read_fw_stats.v1', 'esi-characterstats.read.v1']
EVEAUTH_SCOPES = ALL_SCOPES


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
