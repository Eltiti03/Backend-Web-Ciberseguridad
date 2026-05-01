# src/core/controllers/views_usuarios.py

from django.shortcuts import render
from django.http import JsonResponse

from ..models.usuario import Usuario
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.usuarios.usuario_service import RegistroUsuarioSerializer, get_all_usuarios, get_usuarios_activos, get_all_usuarios, get_usuarios_activos
from ..services.usuarios.login_service import login_usuario
from ..services.usuarios.codigo_service import generar_codigo_verificacion
from ..services.usuarios.email_service import enviar_codigo_verificacion
from ..models import Codigo
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json
from ..services.usuarios.usuario_service import AdminCrearUsuarioSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
def me(request):
    print("USER:", request.user)
    print("AUTH:", request.auth)
    print("COOKIES:", request.COOKIES)

    if not request.user or not request.user.is_authenticated:
        return Response({"authenticated": False}, status=401)

    return Response({
    "authenticated": True,
    "usuario": {
        "id": str(request.user.usuario_id),
        "nombre": request.user.nombre,
        "email": request.user.email,
        "es_administrador": request.user.es_administrador
    }
})

@api_view(["POST"])
def logout(request):
    response = Response({"message": "Sesión cerrada"}, status=200)
    response.set_cookie(
        key="auth_token",
        value="",
        httponly=True,
        secure=True,
        samesite="None",
        max_age=0,        # ← expira inmediatamente
    )
    return response

@api_view(["POST"])
def registro_usuario(request):
    try:
        serializer = RegistroUsuarioSerializer(data=request.data)

        if serializer.is_valid():

            usuario = serializer.save()

            try:
                codigo = generar_codigo_verificacion()
                Codigo.objects.create(usuario=usuario, content=codigo, tipo="VERIFICACION")
                enviar_codigo_verificacion(usuario.email, codigo)
            except Exception as e:
                print("ERROR CORREO:", str(e))

            return Response(
                {"success": True, "result": {"usuario_id": str(usuario.usuario_id), "email": usuario.email}},
                status=status.HTTP_201_CREATED
            )

        return Response({"success": False, "message": serializer.errors}, status=400)

    except BaseException as e:
        print("ERROR BASICO:", type(e).__name__, str(e))
        import traceback
        traceback.print_exc()
        return Response({"success": False, "message": str(e)}, status=500)
    
@api_view(["POST"])
def admin_crear_usuario(request):
    serializer = AdminCrearUsuarioSerializer(data=request.data)

    if serializer.is_valid():
        usuario = serializer.save()
        return Response(
            {
                "success": True,
                "result": {
                    "usuario_id":      str(usuario.usuario_id),
                    "email":           usuario.email,
                    "nombre":          usuario.nombre,
                    "es_administrador": usuario.es_administrador,
                    "verificado":      usuario.verificado,
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"success": False, "message": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["POST"])
def verificar_codigo(request):
    email = request.data.get("email")
    codigo = request.data.get("codigo")
    tipo = request.data.get("tipo")

    if not email or not codigo or not tipo:
        return Response(
            {
                "success": False,
                "message": "email, codigo y tipo son obligatorios"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    codigo_obj = Codigo.objects.filter(
        usuario=usuario,
        content=codigo,
        tipo=tipo,
        used=False
    ).order_by("-fecha_creacion").first()

    if not codigo_obj:
        return Response(
            {
                "success": False,
                "message": "Código inválido o ya usado"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    codigo_obj.used = True
    codigo_obj.save()

    # 🔹 Solo si es verificación activas usuario
    if tipo == "VERIFICACION":
        usuario.verificado = True
        usuario.save()

    return Response(
        {
            "success": True,
            "result": "Código verificado correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
def solicitar_codigo(request):
    email = request.data.get("email")
    tipo = request.data.get("tipo")  # VERIFICACION o RECUPERACION

    if not email or not tipo:
        return Response(
            {
                "success": False,
                "message": "email y tipo son obligatorios"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if tipo not in ["VERIFICACION", "RECUPERACION"]:
        return Response(
            {
                "success": False,
                "message": "Tipo inválido"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    Codigo.objects.filter(
        usuario=usuario,
        tipo=tipo,
        used=False
    ).update(used=True)

    codigo = generar_codigo_verificacion()

    Codigo.objects.create(
        usuario=usuario,
        content=codigo,
        tipo=tipo
    )

    enviar_codigo_verificacion(usuario.email, codigo)

    return Response(
        {
            "success": True,
            "result": f"Código de {tipo.lower()} enviado"
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@authentication_classes([])   # Sin autenticación
@permission_classes([AllowAny])
def login(request):
    usuario, token = login_usuario(request.data)

    response = Response(
        {
            "usuario": {
                "id": str(usuario.usuario_id),
                "email": usuario.email,
                "nombre": usuario.nombre,
                "es_administrador": usuario.es_administrador,
            }
        },
        status=status.HTTP_200_OK
    )

    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,  
        secure=True,       
        samesite="None",  
        max_age=60 * 60 * 24 
    )

    return response

@api_view(['PATCH'])
def eliminar_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(usuario_id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {"success": "false", "message": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    usuario.nombre = "Usuario eliminado"
    usuario.email = f"eliminado_{usuario.usuario_id}@deleted.com" 
    usuario.activo = False
    usuario.save()

    return Response(
        {"success": "true","mensaje": "Usuario eliminado correctamente (inactivo)"},
        status=status.HTTP_200_OK
    )
@api_view(['GET'])
def obtener_usuarios(request):
    usuarios = get_all_usuarios()

    data = [
        {
            "id": str(u.usuario_id),
            "email": u.email,
            "nombre": u.nombre,
            "es_administrador": u.es_administrador,
            "activo": u.activo
        }
        for u in usuarios
    ]

    return Response(
        {"success": True, "result": data},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_usuarios_activos(request):
    usuarios = get_usuarios_activos()

    data = [
        {
            "id": str(u.usuario_id),
            "email": u.email,
            "nombre": u.nombre,
            "es_administrador": u.es_administrador,
            "activo": u.activo
        }
        for u in usuarios
    ]

    return Response(
        {"success": True, "result": data},
        status=status.HTTP_200_OK
    )

@api_view(['PATCH'])
def editar_usuario(request, usuario_id):
    nombre = request.data.get('nombre')
    es_administrador = request.data.get('es_administrador')

    # Ahora ambos campos son opcionales, pero al menos uno debe venir
    if nombre is None and es_administrador is None:
        return Response(
            {
                "success": False,
                "message": "Debes enviar al menos 'nombre' o 'es_administrador'"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(
            usuario_id=usuario_id,
            activo=True
        )
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado o inactivo"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Solo actualiza el campo si viene en el request
    if nombre is not None:
        usuario.nombre = nombre
    if es_administrador is not None:
        usuario.es_administrador = es_administrador

    usuario.save()

    return Response(
        {
            "success": True,
            "result": {
                "usuario_id": str(usuario.usuario_id),
                "nombre": usuario.nombre,
                "es_administrador": usuario.es_administrador
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
def cambiar_password(request):
    email = request.data.get("email")
    nueva_password = request.data.get("password")

    if not email or not nueva_password:
        return Response(
            {
                "success": False,
                "message": "email y password son obligatorios"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    codigo = Codigo.objects.filter(
        usuario=usuario,
        tipo="RECUPERACION"
    ).order_by("-fecha_creacion").first()

    if not codigo or not codigo.used:
        return Response(
            {
                "success": False,
                "message": "Debes verificar el código de recuperación primero"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Cambiar contraseña
    usuario.password_hash = make_password(nueva_password)
    usuario.save()
    return Response(
        {
            "success": True,
            "result": "Contraseña actualizada correctamente"
        },
        status=status.HTTP_200_OK
    )



def health_check_view(request):
    return JsonResponse({"status": "ok"})


