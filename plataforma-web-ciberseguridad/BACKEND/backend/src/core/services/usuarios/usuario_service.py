from rest_framework import serializers

from ...validations.validar_usuario import validar_password

from ...models.usuario import Usuario
from ...serializers.usuarios.usuario_serializer import RegistroUsuarioSerializer
from rest_framework.exceptions import PermissionDenied, NotFound
from django.contrib.auth.hashers import make_password

def registrar_usuario(data):
    serializer = RegistroUsuarioSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def eliminar_usuario(usuario_objetivo, usuario_solicitante):
    if not usuario_solicitante.es_administrador:
        if usuario_objetivo.usuario_id != usuario_solicitante.usuario_id:
            raise PermissionDenied("No tienes permiso para eliminar este usuario")

    if not usuario_objetivo.activo:
        raise NotFound("El usuario ya está inactivo")

    usuario_objetivo.activo = False
    usuario_objetivo.save()

    return usuario_objetivo

def get_usuarios_activos():
    return Usuario.objects.filter(activo=True)

def get_all_usuarios():
    return Usuario.objects.all()

class AdminCrearUsuarioSerializer(serializers.Serializer):
    email            = serializers.EmailField()
    password         = serializers.CharField(write_only=True, min_length=8, validators=[validar_password])
    nombre           = serializers.CharField(max_length=100)
    es_administrador = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        email            = validated_data["email"]
        password         = validated_data["password"]
        nombre           = validated_data["nombre"]
        es_administrador = validated_data.get("es_administrador", False)

        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Este correo ya está registrado"}
            )

        usuario = Usuario.objects.create(
            email=email,
            password_hash=make_password(password),
            nombre=nombre,
            es_administrador=es_administrador,
            verificado=True,  
            activo=True,
        )

        return usuario