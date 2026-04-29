from datetime import timedelta
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Publicacion, Usuario, Comentario
from ..services.publicaciones.publicacion_service import val_tiempo_publicacion
from ..serializers.publicaciones.enums_categorias import CategoriaPublicacion


@api_view(['POST'])
def crear_publicacion(request):
    titulo     = request.data.get("titulo")
    contenido  = request.data.get("contenido")
    usuario_id = request.data.get("usuario_id")
    es_anonima = request.data.get("es_anonima", False)
    categoria  = request.data.get("categoria", None) 

    if not titulo or not contenido or not usuario_id:
        return Response(
            {
                "success": False,
                "message": "titulo, contenido y usuario_id son obligatorios"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(usuario_id=usuario_id, activo=True)
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado o inactivo"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    publicacion = Publicacion.objects.create(
        titulo=titulo,
        contenido=contenido,
        es_anonima=es_anonima,
        usuario=usuario,
        categoria=categoria 
    )

    return Response(
        {
            "success": True,
            "result": {
                "publicacion_id": publicacion.publicacion_id,
                "titulo":         publicacion.titulo,
                "contenido":      publicacion.contenido,
                "es_anonima":     publicacion.es_anonima,
                "fecha_creacion": publicacion.fecha_creacion,
                "editada":        publicacion.editada,
                "usuario_id":     usuario.usuario_id,
                "categoria":      publicacion.categoria,
            }
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
def obtener_categorias_publicacion(request):
    categorias = [
        {"id": choice[0], "label": choice[1]}
        for choice in CategoriaPublicacion.choices
    ]
    return Response({"success": True, "result": categorias})

@api_view(['PATCH'])
def editar_publicacion(request, publicacion_id):
    try:
        publicacion = Publicacion.objects.get(publicacion_id=publicacion_id)
    except Publicacion.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Publicación no encontrada"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Validar tiempo (30 minutos)
    tiempo_limite = val_tiempo_publicacion(30, publicacion_id)

    if timezone.now() > tiempo_limite:
        return Response(
            {
                "success": False,
                "message": "No se puede editar la publicación después de 30 minutos"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    titulo = request.data.get("titulo")
    contenido = request.data.get("contenido")

    if not titulo and not contenido:
        return Response(
            {
                "success": False,
                "message": "Debe enviar al menos titulo o contenido para editar"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if titulo:
        publicacion.titulo = titulo

    if contenido:
        publicacion.contenido = contenido

    publicacion.editada = True
    publicacion.save()

    return Response(
        {
            "success": True,
            "result": {
                "publicacion_id": publicacion.publicacion_id,
                "titulo": publicacion.titulo,
                "contenido": publicacion.contenido,
                "editada": publicacion.editada
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
def eliminar_publicacion(request, publicacion_id):
    try:
        publicacion = Publicacion.objects.get(publicacion_id=publicacion_id)
    except Publicacion.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Publicación no encontrada"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    publicacion.delete()

    return Response(
        {
            "success": True,
            "result": "Publicación eliminada correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_publicaciones_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(usuario_id=usuario_id, activo=True)
    except Usuario.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Usuario no encontrado o inactivo"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    publicaciones = (
        Publicacion.objects
        .filter(usuario=usuario)
        .select_related("usuario")
        .prefetch_related(
            Prefetch(
                "comentarios",
                queryset=Comentario.objects.select_related("usuario").order_by("fecha_creacion")
            )
        )
        .order_by("-fecha_creacion")
    )

    resultado = []

    for pub in publicaciones:
        comentarios_lista = []

        for comentario in pub.comentarios.all():
            comentarios_lista.append({
                "comentario_id": comentario.comentario_id,
                "contenido": comentario.contenido,
                "fecha_creacion": comentario.fecha_creacion,
                "usuario": {
                    "usuario_id": comentario.usuario.usuario_id
                }
            })

        resultado.append({
            "publicacion_id": pub.publicacion_id,
            "titulo": pub.titulo,
            "contenido": pub.contenido,
            "es_anonima": pub.es_anonima,
            "fecha_creacion": pub.fecha_creacion,
            "editada": pub.editada,
            "usuario": None if pub.es_anonima else {
                "usuario_id": pub.usuario.usuario_id
            },
            "comentarios": comentarios_lista
        })

    return Response(
        {
            "success": True,
            "result": resultado
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_publicaciones(request):
    publicaciones = Publicacion.objects.prefetch_related('comentarios').all()  

    titulo = request.GET.get("titulo")
    usuario_id = request.GET.get("usuario_id")

    if titulo:
        publicaciones = publicaciones.filter(titulo__icontains=titulo)
    if usuario_id:
        publicaciones = publicaciones.filter(usuario__usuario_id=usuario_id)

    data = [
        {
            "publicacion_id": str(p.publicacion_id),
            "titulo": p.titulo,
            "contenido": p.contenido,
            "fecha_creacion": p.fecha_creacion,
            "usuario": None if p.es_anonima else {
                "usuario_id": str(p.usuario.usuario_id),
                "nombre": p.usuario.nombre
            },
            "es_anonima": p.es_anonima,
            "comentarios": [         
                {
                    "comentario_id": str(c.comentario_id),
                    "contenido": c.contenido,
                    "fecha_creacion": c.fecha_creacion,
                    "usuario": {
                        "usuario_id": str(c.usuario.usuario_id),
                        "nombre": c.usuario.nombre
                    } if c.usuario else None
                }
                for c in p.comentarios.all()
            ]
        }
        for p in publicaciones
    ]

    return Response(
        {"success": True, "result": data},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_publicacion(request, publicacion_id):
    try:
        p = Publicacion.objects.get(publicacion_id=publicacion_id)
    except Publicacion.DoesNotExist:
        return Response(
            {"success": False, "message": "Publicación no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = {
        "publicacion_id": str(p.publicacion_id),
        "titulo": p.titulo,
        "contenido": p.contenido,
        "fecha_creacion": p.fecha_creacion,
        "usuario": None if p.es_anonima else {
            "usuario_id": str(p.usuario.usuario_id),
            "nombre": p.usuario.nombre
        },
        "es_anonima": p.es_anonima,
        "comentarios": list(p.comentarios.values("comentario_id", "contenido", "fecha_creacion", "usuario__usuario_id", "usuario__nombre"))
    }

    return Response(
        {"success": True, "result": data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def crear_comentario(request):
    usuario_id = request.data.get("usuario_id")
    publicacion_id = request.data.get("publicacion_id")
    contenido = request.data.get("contenido")

    if not usuario_id or not publicacion_id or not contenido:
        return Response(
            {
                "success": False,
                "message": "usuario_id, publicacion_id y contenido son obligatorios"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(usuario_id=usuario_id, activo=True)
    except Usuario.DoesNotExist:
        return Response(
            {"success": False, "message": "Usuario no encontrado o inactivo"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        publicacion = Publicacion.objects.get(publicacion_id=publicacion_id)
    except Publicacion.DoesNotExist:
        return Response(
            {"success": False, "message": "Publicación no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    comentario = Comentario.objects.create(
        contenido=contenido,
        usuario=usuario,
        publicacion=publicacion
    )

    return Response(
        {
            "success": True,
            "message": "Comentario creado correctamente",
            "result": {
                "comentario_id": comentario.comentario_id,
                "contenido": comentario.contenido,
                "fecha_creacion": comentario.fecha_creacion
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
def eliminar_comentario(request, comentario_id):
    usuario_id = request.data.get("usuario_id")

    if not usuario_id:
        return Response(
            {"success": False, "message": "usuario_id es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        comentario = Comentario.objects.get(comentario_id=comentario_id)
    except Comentario.DoesNotExist:
        return Response(
            {"success": False, "message": "Comentario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    if str(comentario.usuario.usuario_id) != str(usuario_id):
        return Response(
            {"success": False, "message": "No tienes permiso para eliminar este comentario"},
            status=status.HTTP_403_FORBIDDEN
        )

    comentario.delete()

    return Response(
        {
            "success": True,
            "message": "Comentario eliminado correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(['PATCH'])
def editar_comentario(request, comentario_id):
    usuario_id = request.data.get("usuario_id")
    nuevo_contenido = request.data.get("contenido")

    if not usuario_id or not nuevo_contenido:
        return Response(
            {"success": False, "message": "usuario_id y contenido son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        comentario = Comentario.objects.get(comentario_id=comentario_id)
    except Comentario.DoesNotExist:
        return Response(
            {"success": False, "message": "Comentario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    if str(comentario.usuario.usuario_id) != str(usuario_id):
        return Response(
            {"success": False, "message": "No tienes permiso para editar este comentario"},
            status=status.HTTP_403_FORBIDDEN
        )

    comentario.contenido = nuevo_contenido
    comentario.save()

    return Response(
        {
            "success": True,
            "message": "Comentario actualizado correctamente"
        },
        status=status.HTTP_200_OK
    )