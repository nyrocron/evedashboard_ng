from datetime import datetime, timedelta
from pytz import UTC

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

import dateutil.parser
from django.utils.crypto import get_random_string

from eveauth import simple_sso


class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    valid_until = models.DateTimeField()
    character_id = models.IntegerField(unique=True)
    character_name = models.CharField(max_length=200)

    def get_access_token(self, valid_for=60):
        """
        Get an access token that is valid for at least the given number of seconds.

        Will trigger a refresh if necessary.
        """
        if not (0 < valid_for <= 120):
            raise ValueError("valid_for must be greate than 0 and less than or equal to 120.")

        validity_buffer = timedelta(seconds=valid_for)
        if self.access_token is None or self.valid_until - validity_buffer < datetime.now():
            self.refresh()

        raise NotImplementedError()

    def refresh(self):
        token_info = simple_sso.get_access_token(
            settings.EVESSO_CLIENT_ID,
            settings.EVESSO_SECRET_KEY,
            self.refresh_token,
        )

        self.valid_until = datetime.now() + timedelta(seconds=token_info["expires_in"])
        self.access_token = token_info["access_token"]

        self.save()

    @staticmethod
    def from_oauth(user, auth_code):
        token_info = simple_sso.get_access_token(
            settings.EVESSO_CLIENT_ID,
            settings.EVESSO_SECRET_KEY,
            auth_code,
        )

        aux_info = simple_sso.verify_token(token_info["access_token"])

        # TODO: delete existing entries with same character id

        token = AccessToken(user=user)
        token.refresh_token = token_info["refresh_token"]
        token.access_token = token_info["access_token"]
        expiry_date = dateutil.parser.isoparse(aux_info["ExpiresOn"])
        expiry_date.replace(tzinfo=UTC)
        token.valid_until = expiry_date
        token.character_id = aux_info["CharacterID"]
        token.character_name = aux_info["CharacterName"]
        token.save()

        return token


def get_auth_request_key():
    return get_random_string(length=64)


class AuthenticationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True, default=get_auth_request_key)
    created = models.DateTimeField(auto_now_add=True)
