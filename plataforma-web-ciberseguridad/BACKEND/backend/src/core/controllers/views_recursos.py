from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.recursos.categorias_service import all_categorias_recursos
from ..models import CategoriaRecurso, RecursoEducativo


@api_view(['POST'])
def crear_categoria_recurso(request):
    nombre = request.data.get('nombre')
    descripcion = request.data.get('descripcion')

    if not nombre:
        return Response(
            {
                "success": False,
                "message": "El campo 'nombre' es obligatorio"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    categoria = CategoriaRecurso.objects.create(
        nombre=nombre,
        descripcion=descripcion
    )

    return Response(
        {
            "success": True,
            "result": {
                "categoria_id": str(categoria.categoria_id),
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion
            }
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['DELETE'])
def eliminar_categoria_recurso(request, categoria_id):
    try:
        categoria = CategoriaRecurso.objects.get(categoria_id=categoria_id)
    except CategoriaRecurso.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Categoría no encontrada"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    categoria.delete()

    return Response(
        {
            "success": True,
            "result": "Categoría eliminada correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_categorias_recurso(request):
    res = all_categorias_recursos()
    data = [
        {
            "categoria_id": str(u.categoria_id),
            "nombre": u.nombre,
            "descripcion": u.descripcion
        }for u in res
    ]

    return Response(
        {"success": True, "result": data},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def crear_recurso(request):
    titulo = request.data.get("titulo")
    descripcion = request.data.get("descripcion")
    url_recurso = request.data.get("url_recurso")
    tipo_recurso = request.data.get("tipo_recurso")
    es_publico = request.data.get("es_publico", True)
    categoria_id = request.data.get("categoria_id")

    if not titulo:
        return Response(
            {"success": False, "message": "El titulo es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    categoria = None
    if categoria_id:
        try:
            categoria = CategoriaRecurso.objects.get(categoria_id=categoria_id)
        except CategoriaRecurso.DoesNotExist:
            return Response(
                {"success": False, "message": "Categoría no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

    recurso = RecursoEducativo.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        url_recurso=url_recurso,
        tipo_recurso=tipo_recurso,
        es_publico=es_publico,
        categoria=categoria
    )

    return Response(
        {
            "success": True,
            "message": "Recurso creado correctamente",
            "result": {
                "recurso_id": recurso.recurso_id
            }
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['PATCH'])
def editar_recurso(request, recurso_id):
    try:
        recurso = RecursoEducativo.objects.get(recurso_id=recurso_id)
    except RecursoEducativo.DoesNotExist:
        return Response(
            {"success": False, "message": "Recurso no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    titulo = request.data.get("titulo")
    descripcion = request.data.get("descripcion")
    url_recurso = request.data.get("url_recurso")
    tipo_recurso = request.data.get("tipo_recurso")
    es_publico = request.data.get("es_publico")
    categoria_id = request.data.get("categoria_id")

    if titulo is not None:
        recurso.titulo = titulo

    if descripcion is not None:
        recurso.descripcion = descripcion

    if url_recurso is not None:
        recurso.url_recurso = url_recurso

    if tipo_recurso is not None:
        recurso.tipo_recurso = tipo_recurso

    if es_publico is not None:
        recurso.es_publico = es_publico

    if categoria_id is not None:
        if categoria_id == "":
            recurso.categoria = None
        else:
            try:
                categoria = CategoriaRecurso.objects.get(categoria_id=categoria_id)
                recurso.categoria = categoria
            except CategoriaRecurso.DoesNotExist:
                return Response(
                    {"success": False, "message": "Categoría no encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )

    recurso.save()

    return Response(
        {
            "success": True,
            "message": "Recurso actualizado correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
def eliminar_recurso(request, recurso_id):
    try:
        recurso = RecursoEducativo.objects.get(recurso_id=recurso_id)
    except RecursoEducativo.DoesNotExist:
        return Response(
            {"success": False, "message": "Recurso no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    recurso.delete()

    return Response(
        {
            "success": True,
            "message": "Recurso eliminado correctamente"
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def obtener_recursos(request):
    categoria_id = request.query_params.get("categoria_id")
    incluir_privados = request.query_params.get("incluir_privados", "false").lower() == "true"

    recursos = RecursoEducativo.objects.all()

    if not incluir_privados:
        recursos = recursos.filter(es_publico=True)

    if categoria_id:
        recursos = recursos.filter(categoria__categoria_id=categoria_id)

    recursos = recursos.select_related("categoria").order_by("-fecha_publicacion")

    resultado = []

    for recurso in recursos:
        resultado.append({
            "recurso_id": recurso.recurso_id,
            "titulo": recurso.titulo,
            "descripcion": recurso.descripcion,
            "url_recurso": recurso.url_recurso,
            "tipo_recurso": recurso.tipo_recurso,
            "fecha_publicacion": recurso.fecha_publicacion,
            "es_publico": recurso.es_publico,
            "categoria": {
                "categoria_id": recurso.categoria.categoria_id,
                "nombre": recurso.categoria.nombre
            } if recurso.categoria else None
        })

    return Response(
        {
            "success": True,
            "result": resultado
        },
        status=status.HTTP_200_OK
    )

