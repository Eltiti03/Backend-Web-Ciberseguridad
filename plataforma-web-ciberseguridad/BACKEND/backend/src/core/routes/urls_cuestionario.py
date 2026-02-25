from django.urls import path

from ..controllers.views_cuestionarios import crear_cuestionario, eliminar_cuestionario, iniciar_intento, obtener_cuestionarios, crear_pregunta, editar_pregunta,eliminar_pregunta,obtener_preguntas_cuestionario, crear_opcion, editar_opcion, eliminar_opcion, responder_pregunta

urlpatterns = [
    path('cuestionario/crear/', crear_cuestionario),
    path('cuestionario/obtener/all/', obtener_cuestionarios),
    path('cuestionario/eliminar/<uuid:cuestionario_id>/', eliminar_cuestionario),
    path('cuestionario/pregunta/crear/', crear_pregunta ),
    path('cuestionario/pregunta/editar/<uuid:pregunta_id>/', editar_pregunta),
    path('cuestionario/pregunta/eliminar/<uuid:pregunta_id>/', eliminar_pregunta),
    path('cuestionario/pregunta/obtener/<uuid:cuestionario_id>/', obtener_preguntas_cuestionario),
    path('cuestionario/pregunta/opcion/crear/', crear_opcion),
    path('cuestionario/pregunta/opcion/editar/<uuid:opcion_id>/', editar_opcion),
    path('cuestionario/pregunta/opcion/eliminar/<uuid:opcion_id>/', eliminar_opcion),
    path('cuestionario/intento/iniciar/', iniciar_intento),
    path('cuestionario/intento/responder/', responder_pregunta),
]