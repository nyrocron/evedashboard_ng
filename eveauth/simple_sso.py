# Copyright 2018 Florian Tautz

from urllib.parse import urlencode
import json

import requests


def login_link(redirect_uri, client_id, scopes, state):
    return "https://login.eveonline.com/oauth/authorize?" + urlencode({
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "scope": " ".join(scopes),
        "state": state,
    })


def token_from_authcode(client_id, secret_key, authorization_code):
    url = "https://login.eveonline.com/oauth/token"
    response = requests.post(url, {
        "grant_type": "authorization_code",
        "code": authorization_code
    }, auth=(client_id, secret_key))
    return json.loads(response.content)


def token_from_refresh(client_id, secret_key, refresh_token):
    url = "https://login.eveonline.com/oauth/token"
    request = requests.post(url, {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }, auth=(client_id, secret_key))
    return json.loads(request.content)


def verify_token(access_token):
    response = requests.get("https://esi.evetech.net/verify/", headers={
        "Authorization": f"Bearer {access_token}",
    })
    token_info = json.loads(response.content)
    return token_info
