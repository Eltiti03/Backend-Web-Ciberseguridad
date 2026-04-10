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
            print("USUARIO AUTENTICADO:", usuario)
        except Exception as e:
            print("ERROR EXACTO:", str(e))  # ← agrega esto
            raise AuthenticationFailed("Token inválido")

        return (usuario, None)