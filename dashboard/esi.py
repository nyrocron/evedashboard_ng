import json
from hashlib import md5
import logging

from django.core.cache import caches
from django.utils.timezone import now

import dateutil.parser
import requests

import eveauth.models


esi_cache = caches['esi']
ESI_BASEURL = "https://esi.evetech.net/latest/"
logger = logging.getLogger(__name__)


class ESIError(Exception):
    pass


def esi_query(path):
    logger.debug(f"ESI query: {path}")
    result = esi_cache.get(path)

    if result is None:
        response = requests.get(ESI_BASEURL + path)

        if response.status_code != 200:
            raise ESIError(str(path))

        try:
            expires_at = dateutil.parser.parse(response.headers['expires'])
            cache_time = (expires_at - now()).total_seconds()
        except KeyError:
            cache_time = 60

        result = response.content
        esi_cache.set(path, result, cache_time)

    return result


def entity_name(id):
    cache_key = f'entity_name:{id}'
    result = esi_cache.get(cache_key)

    if result is None:
        try:
            entity = character(id)
        except ESIError:
            try:
                entity = corporation(id)
            except ESIError:
                try:
                    entity = alliance(id)
                except ESIError:
                    raise

        result = entity['name']
        esi_cache.set(cache_key, result, 259200)

    return result


def esi_auth_query(token, path, **params):
    logger.debug(f"ESI authenticated query for '{token.character_name}': {path}")
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

        if response.status_code != 200:
            raise ESIError()

        try:
            expires_at = dateutil.parser.parse(response.headers['expires'])
            cache_time = (expires_at - now()).total_seconds()
        except KeyError:
            cache_time = 60

        result = response.content
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


def mail_list(token):
    return json.loads(esi_auth_query(token, 'characters/{character_id}/mail/'))


def mail_content(token, mail_id):
    return json.loads(esi_auth_query(token, 'characters/{character_id}/mail/{mail_id}/', mail_id=mail_id))

