from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils.validar_token import validar_token

class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("auth_token")

        if not token:
            return None

        try:
            usuario = validar_token(token)
            return (usuario, None)
        except Exception as e:
            print("ERROR EXACTO:", str(e))
            return None  # ← Era "raise", cámbialo a "return None"