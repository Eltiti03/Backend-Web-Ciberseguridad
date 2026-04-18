from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.cuestionarios.cuestionarios_service import all_cuestionarios
from ..models import Cuestionario, Pregunta, OpcionRespuesta, RespuestaUsuario, IntentoCuestionario, Usuario
from django.db.models import Sum
from django.db.models import Prefetch

@api_view(['POST'])
def crear_cuestionario(request):
    titulo = request.data.get('titulo')
    descripcion = request.data.get('descripcion')
    tiempo_limite_minutos = request.data.get('tiempo_limite_minutos', 0)
    es_activo = request.data.get('es_activo')

    if not titulo:
        return Response(
            {"success": False, "message": "El campo 'titulo' es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tiempo_limite_minutos = int(tiempo_limite_minutos)
        if tiempo_limite_minutos < 0:
            raise ValueError
    except ValueError:
        return Response(
            {"success": False, "message": "El tiempo_limite_minutos debe ser mayor o igual a 0"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if es_activo is None:
        es_activo = True
    else:
        if isinstance(es_activo, bool):
            pass
        elif str(es_activo).lower() == "true":
            es_activo = True
        elif str(es_activo).lower() == "false":
            es_activo = False
        else:
            return Response(
                {"success": False, "message": "El campo 'es_activo' debe ser true o false"},
                status=status.HTTP_400_BAD_REQUEST
            )

    cuestionario = Cuestionario.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        tiempo_limite_minutos=tiempo_limite_minutos,
        es_activo=es_activo
    )

    return Response(
        {
            "success": True,
            "result": {
                "cuestionario_id": str(cuestionario.cuestionario_id),
                "titulo": cuestionario.titulo,
                "descripcion": cuestionario.descripcion,
                "es_activo": cuestionario.es_activo,
                "tiempo_limite_minutos": cuestionario.tiempo_limite_minutos
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PATCH'])
def editar_cuestionario(request, cuestionario_id):
    try:
        cuestionario = Cuestionario.objects.get(cuestionario_id=cuestionario_id)
    except Cuestionario.DoesNotExist:
        return Response(
            {"success": False, "message": "Cuestionario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    titulo = request.data.get("titulo")
    descripcion = request.data.get("descripcion")
    tiempo_limite_minutos = request.data.get("tiempo_limite_minutos")
    es_activo = request.data.get("es_activo")

    if titulo is not None:
        cuestionario.titulo = titulo
    if descripcion is not None:
        cuestionario.descripcion = descripcion
    if tiempo_limite_minutos is not None:
        try:
            tiempo_limite_minutos = int(tiempo_limite_minutos)
            if tiempo_limite_minutos < 0:
                raise ValueError
            cuestionario.tiempo_limite_minutos = tiempo_limite_minutos
        except ValueError:
            return Response(
                {"success": False, "message": "El tiempo_limite_minutos debe ser mayor o igual a 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
    if es_activo is not None:
        if isinstance(es_activo, bool):
            cuestionario.es_activo = es_activo
        elif str(es_activo).lower() == "true":
            cuestionario.es_activo = True
        elif str(es_activo).lower() == "false":
            cuestionario.es_activo = False

    cuestionario.save()

    return Response(
        {
            "success": True,
            "message": "Cuestionario actualizado correctamente",
            "result": {
                "cuestionario_id": str(cuestionario.cuestionario_id),
                "titulo": cuestionario.titulo,
                "descripcion": cuestionario.descripcion,
                "es_activo": cuestionario.es_activo,
                "tiempo_limite_minutos": cuestionario.tiempo_limite_minutos
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def obtener_cuestionarios(request):
    cuestionarios = Cuestionario.objects.prefetch_related(
        Prefetch(
            "preguntas",
            queryset=Pregunta.objects.prefetch_related("opciones")
        )
    )

    data = []
    for c in cuestionarios:
        preguntas_data = []
        for p in c.preguntas.all():
            opciones_data = [
                {
                    "opcion_id": str(o.opcion_id),
                    "texto": o.texto,
                    "es_correcta": o.es_correcta
                }
                for o in p.opciones.all()
            ]
            preguntas_data.append({
                "pregunta_id": str(p.pregunta_id),
                "enunciado": p.enunciado,
                "puntos": p.puntos,
                "opciones": opciones_data
            })

        data.append({
            "cuestionario_id": str(c.cuestionario_id),
            "titulo": c.titulo,
            "descripcion": c.descripcion,
            "es_activo": c.es_activo,
            "tiempo_limite_minutos": c.tiempo_limite_minutos,
            "preguntas": preguntas_data
        })

    return Response({"success": True, "result": data}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def eliminar_cuestionario(request, cuestionario_id):
    try:
        cuestionario = Cuestionario.objects.get(cuestionario_id=cuestionario_id)
    except Cuestionario.DoesNotExist:
        return Response(
            {"success": False, "message": "Cuestionario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    cuestionario.delete()
    return Response(
        {"success": True, "result": "Cuestionario eliminado correctamente"},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def crear_pregunta(request):
    enunciado = request.data.get("enunciado")
    puntos = request.data.get("puntos", 1)
    cuestionario_id = request.data.get("cuestionario_id")

    if not enunciado or not cuestionario_id:
        return Response(
            {"success": False, "message": "enunciado y cuestionario_id son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cuestionario = Cuestionario.objects.get(cuestionario_id=cuestionario_id)
    except Cuestionario.DoesNotExist:
        return Response(
            {"success": False, "message": "Cuestionario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    pregunta = Pregunta.objects.create(
        enunciado=enunciado,
        puntos=puntos,
        cuestionario=cuestionario
    )

    return Response(
        {
            "success": True,
            "message": "Pregunta creada correctamente",
            "result": {"pregunta_id": str(pregunta.pregunta_id)}
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PATCH'])
def editar_pregunta(request, pregunta_id):
    try:
        pregunta = Pregunta.objects.get(pregunta_id=pregunta_id)
    except Pregunta.DoesNotExist:
        return Response(
            {"success": False, "message": "Pregunta no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    enunciado = request.data.get("enunciado")
    puntos = request.data.get("puntos")

    if enunciado is not None:
        pregunta.enunciado = enunciado
    if puntos is not None:
        pregunta.puntos = puntos

    pregunta.save()
    return Response({"success": True, "message": "Pregunta actualizada correctamente"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def eliminar_pregunta(request, pregunta_id):
    try:
        pregunta = Pregunta.objects.get(pregunta_id=pregunta_id)
    except Pregunta.DoesNotExist:
        return Response(
            {"success": False, "message": "Pregunta no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    pregunta.delete()
    return Response({"success": True, "message": "Pregunta eliminada correctamente"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def obtener_preguntas_cuestionario(request, cuestionario_id):
    try:
        cuestionario = Cuestionario.objects.get(cuestionario_id=cuestionario_id)
    except Cuestionario.DoesNotExist:
        return Response(
            {"success": False, "message": "Cuestionario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    preguntas = Pregunta.objects.filter(cuestionario=cuestionario).order_by("pregunta_id")
    resultado = [
        {"pregunta_id": str(p.pregunta_id), "enunciado": p.enunciado, "puntos": p.puntos}
        for p in preguntas
    ]

    return Response(
        {"success": True, "cuestionario_id": str(cuestionario_id), "result": resultado},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def crear_opcion(request):
    texto = request.data.get("texto")
    pregunta_id = request.data.get("pregunta_id")
    es_correcta = request.data.get("es_correcta", False)
    retroalimentacion = request.data.get("retroalimentacion")

    if not texto or not pregunta_id:
        return Response(
            {"success": False, "message": "texto y pregunta_id son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        pregunta = Pregunta.objects.get(pregunta_id=pregunta_id)
    except Pregunta.DoesNotExist:
        return Response(
            {"success": False, "message": "Pregunta no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    if es_correcta:
        OpcionRespuesta.objects.filter(pregunta=pregunta, es_correcta=True).update(es_correcta=False)

    opcion = OpcionRespuesta.objects.create(
        texto=texto,
        es_correcta=es_correcta,
        retroalimentacion=retroalimentacion,
        pregunta=pregunta
    )

    return Response(
        {
            "success": True,
            "message": "Opción creada correctamente",
            "result": {"opcion_id": str(opcion.opcion_id)}
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PATCH'])
def editar_opcion(request, opcion_id):
    try:
        opcion = OpcionRespuesta.objects.get(opcion_id=opcion_id)
    except OpcionRespuesta.DoesNotExist:
        return Response(
            {"success": False, "message": "Opción no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    texto = request.data.get("texto")
    es_correcta = request.data.get("es_correcta")
    retroalimentacion = request.data.get("retroalimentacion")

    if texto is not None:
        opcion.texto = texto
    if retroalimentacion is not None:
        opcion.retroalimentacion = retroalimentacion
    if es_correcta is not None:
        if es_correcta:
            OpcionRespuesta.objects.filter(
                pregunta=opcion.pregunta, es_correcta=True
            ).exclude(opcion_id=opcion_id).update(es_correcta=False)
        opcion.es_correcta = es_correcta

    opcion.save()
    return Response({"success": True, "message": "Opción actualizada correctamente"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def eliminar_opcion(request, opcion_id):
    try:
        opcion = OpcionRespuesta.objects.get(opcion_id=opcion_id)
    except OpcionRespuesta.DoesNotExist:
        return Response(
            {"success": False, "message": "Opción no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    opcion.delete()
    return Response({"success": True, "message": "Opción eliminada correctamente"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def iniciar_intento(request):
    usuario_id = request.data.get("usuario_id")
    cuestionario_id = request.data.get("cuestionario_id")

    if not usuario_id or not cuestionario_id:
        return Response(
            {"success": False, "message": "usuario_id y cuestionario_id son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(usuario_id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"success": False, "message": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        cuestionario = Cuestionario.objects.get(cuestionario_id=cuestionario_id)
    except Cuestionario.DoesNotExist:
        return Response({"success": False, "message": "Cuestionario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    intento = IntentoCuestionario.objects.create(usuario=usuario, cuestionario=cuestionario)

    return Response(
        {"success": True, "message": "Intento iniciado correctamente", "intento_id": str(intento.intento_id)},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def responder_pregunta(request):
    intento_id = request.data.get("intento_id")
    pregunta_id = request.data.get("pregunta_id")
    opcion_id = request.data.get("opcion_id")

    if not intento_id or not pregunta_id or not opcion_id:
        return Response(
            {"success": False, "message": "intento_id, pregunta_id y opcion_id son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        intento = IntentoCuestionario.objects.get(intento_id=intento_id)
    except IntentoCuestionario.DoesNotExist:
        return Response({"success": False, "message": "Intento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        pregunta = Pregunta.objects.get(pregunta_id=pregunta_id)
    except Pregunta.DoesNotExist:
        return Response({"success": False, "message": "Pregunta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if pregunta.cuestionario != intento.cuestionario:
        return Response(
            {"success": False, "message": "La pregunta no pertenece al cuestionario del intento"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        opcion = OpcionRespuesta.objects.get(opcion_id=opcion_id)
    except OpcionRespuesta.DoesNotExist:
        return Response({"success": False, "message": "Opción no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if opcion.pregunta != pregunta:
        return Response(
            {"success": False, "message": "La opción no pertenece a la pregunta"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if RespuestaUsuario.objects.filter(intento=intento, pregunta=pregunta).exists():
        return Response(
            {"success": False, "message": "Ya respondiste esta pregunta en este intento"},
            status=status.HTTP_400_BAD_REQUEST
        )

    RespuestaUsuario.objects.create(intento=intento, pregunta=pregunta, opcion_seleccionada=opcion)

    total = RespuestaUsuario.objects.filter(
        intento=intento, opcion_seleccionada__es_correcta=True
    ).aggregate(total=Sum("pregunta__puntos"))["total"] or 0

    intento.puntaje_total = total
    intento.save()

    return Response(
        {"success": True, "message": "Respuesta registrada correctamente", "puntaje_actual": total},
        status=status.HTTP_201_CREATED
    )
