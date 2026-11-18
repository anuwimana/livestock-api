import hashlib

import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Profile


class SupabaseUser:
    is_authenticated = True

    def __init__(self, profile):
        self.id = profile.id
        self.role = profile.role
        self.full_name = profile.full_name


def get_bearer_token(request):
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        return header[7:]
    return None


def fetch_supabase_user(token):
    key = 'sbuser:' + hashlib.sha256(token.encode()).hexdigest()
    cached = cache.get(key)
    if cached:
        return cached

    response = None
    for _ in range(2):
        try:
            response = requests.get(
                f'{settings.SUPABASE_URL}/auth/v1/user',
                headers={'Authorization': f'Bearer {token}',
                         'apikey': settings.SUPABASE_KEY},
                timeout=30,
            )
            break
        except requests.RequestException:
            continue

    if response is None:
        raise AuthenticationFailed('Cannot reach the auth service.')
    if response.status_code != 200:
        raise AuthenticationFailed('Invalid or expired token.')

    data = response.json()
    cache.set(key, data, 300)
    return data


class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = get_bearer_token(request)
        if not token:
            return None
        data = fetch_supabase_user(token)
        try:
            profile = Profile.objects.get(pk=data['id'])
        except Profile.DoesNotExist:
            raise AuthenticationFailed('No profile found for this user.')
        return (SupabaseUser(profile), token)

    def authenticate_header(self, request):
        return 'Bearer'