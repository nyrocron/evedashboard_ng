import json
from hashlib import md5

from django.core.cache import caches
from django.utils.timezone import now

import dateutil.parser
import requests

import eveauth.models


esi_cache = caches['esi']
ESI_BASEURL = "https://esi.evetech.net/latest/"


def esi_query(path):
    result = esi_cache.get(path)

    if result is None:
        response = requests.get(ESI_BASEURL + path)

        try:
            expires_at = dateutil.parser.parse(response.headers['expires'])
            cache_time = (expires_at - now()).total_seconds()
        except KeyError:
            cache_time = 60

        result = response.content
        dateutil.parser.parse(response.headers['expires'])
        esi_cache.set(path, result, cache_time)

    return result


def esi_auth_query(token, path, **params):
    hasher = md5()
    hasher.update(f"{path}\n".encode('utf-8'))
    hasher.update(f"{token.character_id}\n".encode('utf-8'))
    for key, value in sorted(params.items()):
        hasher.update(f"{key}={value}\n".encode('utf-8'))
    cache_key = hasher.hexdigest()

    result = esi_cache.get(cache_key)

    if result is None:
        response = requests.get(ESI_BASEURL + path.format(character_id=token.character_id, **params), params={
            "token": token.get_access_token(),
        })

        try:
            expires_at = dateutil.parser.parse(response.headers['expires'])
            cache_time = (expires_at - now()).total_seconds()
        except KeyError:
            cache_time = 60

        result = response.content
        dateutil.parser.parse(response.headers['expires'])
        esi_cache.set(cache_key, result, cache_time)

    return result


def wallet_balance(token: eveauth.models.AccessToken):
    return float(esi_auth_query(token, 'characters/{character_id}/wallet/'))


def skillqueue(token: eveauth.models.AccessToken):
    return json.loads(esi_auth_query(token, 'characters/{character_id}/skillqueue/'))


def skills(token: eveauth.models.AccessToken):
    return json.loads(esi_auth_query(token, 'characters/{character_id}/skills/'))


def character(character_id):
    return json.loads(esi_query(f"characters/{character_id}/"))


def corporation(corporation_id):
    return json.loads(esi_query(f"corporations/{corporation_id}/"))


def alliance(alliance_id):
    return json.loads(esi_query(f"alliances/{alliance_id}/"))
