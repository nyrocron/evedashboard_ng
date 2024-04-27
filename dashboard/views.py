import dateutil.parser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now

from dashboard import esi
from dashboard import evestatic


@login_required
def index(request):
    return render(request, 'dashboard/dashboard.html', {
        'characters': [{
            'id': character.character_id,
            'name': character.character_name,
        } for character in request.user.accesstoken_set.all()],
    })


@login_required
def character(request, id):
    token = request.user.accesstoken_set.get(character_id=id)
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

    mail_list = esi.mail_list(token)
    context['new_mail'] = any("is_read" not in mail or not mail["is_read"] for mail in mail_list)

    return render(request, 'dashboard/character_tile.html', context)


@login_required
def character_mail_list(request, id):
    token = request.user.accesstoken_set.get(character_id=id)
    mail_list = esi.mail_list(token)

    mails = []
    for mail in mail_list:
        mails.append({
            'unread': 'is_read' not in mail or not mail['is_read'],
            'timestamp': mail['timestamp'],
            'from': esi.entity_name(mail['from']),
            'subject': mail['subject'],
        })

    return render(request, 'dashboard/mail_list.html', {'mails': mails})
