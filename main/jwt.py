from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

def get_access_token(user):
    access_token = AccessToken.for_user(user)
    access_token['exp'] = datetime.now() + timedelta(days=7)
    return str(access_token)

def get_refresh_token(user):
    refresh_token = RefreshToken.for_user(user)
    refresh_token['exp'] = datetime.now() + timedelta(days=30)
    return str(refresh_token)
