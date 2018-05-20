from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now

import dateutil.parser

from dashboard import esi
from dashboard import evestatic


@login_required
def index(request):

    characters = []
    for token in request.user.accesstoken_set.all():
        skills = esi.skills(token)

        character_info = esi.character(token.character_id)
        corporation_parts = []
        corporation_info = esi.corporation(character_info['corporation_id'])
        corporation_parts.append(f"[{corporation_info['name']}]")
        if 'alliance_id' in corporation_info:
            alliance_info = esi.alliance(corporation_info['alliance_id'])
            corporation_parts.append(f"<{alliance_info['name']}>")

        context = {
            'id': token.character_id,
            'name': token.character_name,
            'wallet_balance': esi.wallet_balance(token),
            'total_sp': skills['total_sp'],
            'corporation': " ".join(corporation_parts)
        }

        skillqueue = esi.skillqueue(token)
        if len(skillqueue) > 0 and 'finish_date' in skillqueue[0]:
            context['queue_active'] = True
            context['queue_end'] = dateutil.parser.parse(skillqueue[-1]['finish_date'])
            context['queue_duration'] = context['queue_end'] - now()
            context['training_skill'] = evestatic.skill_name(skillqueue[0]['skill_id'])
            context['training_level'] = skillqueue[0]['finished_level']
        else:
            context['queue_active'] = False

        characters.append(context)

    return render(request, 'dashboard/dashboard.html', {
        'characters': characters,
    })
