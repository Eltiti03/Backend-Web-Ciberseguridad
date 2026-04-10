import jwt
import uuid
from django.conf import settings
from ...models import Usuario
from rest_framework.exceptions import AuthenticationFailed

def validar_token(token):
    try:
        # Decodificamos asegurando que usamos la SECRET_KEY del proyecto
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id_str = payload.get("user_id")
        if not user_id_str:
            print("Error 1")
            raise AuthenticationFailed("El token no contiene el ID de usuario")

        # IMPORTANTE: Convertimos el string a un objeto UUID real
        try:
            user_id_obj = uuid.UUID(user_id_str)
            # Buscamos usando el objeto UUID
            usuario = Usuario.objects.get(usuario_id=user_id_obj)
            
            return usuario
        except (ValueError, Usuario.DoesNotExist):
            print("Error 2")
            raise AuthenticationFailed("Usuario no encontrado en la base de datos")

    except jwt.ExpiredSignatureError:
        print("Error 3")
        raise AuthenticationFailed("El token ha expirado")
    except jwt.InvalidTokenError as e:
        # Esto te dirá en la consola si el problema es la firma (Signature)
        print(f"Error de JWT: {e}")
        print("Error 4") 
        raise AuthenticationFailed(f"Token inválido: {str(e)}")