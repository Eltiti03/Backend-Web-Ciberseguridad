from django.urls import path

from ..controllers.views_publicacion import crear_comentario, crear_publicacion, editar_comentario, editar_publicacion, eliminar_comentario, eliminar_publicacion, obtener_publicacion, obtener_publicaciones, obtener_publicaciones_usuario

urlpatterns = [

    path('publicacion/all/', obtener_publicaciones),
    path('publicacion/<uuid:publicacion_id>/', obtener_publicacion),
    path('publicacion/crear/', crear_publicacion),
    path('publicacion/editar/<uuid:publicacion_id>/', editar_publicacion),
    path('publicacion/eliminar/<uuid:publicacion_id>/', eliminar_publicacion),
    path('publicacion/obtener/usuario/<uuid:usuario_id>/', obtener_publicaciones_usuario),
    path('publicacion/comentario/crear/', crear_comentario),
    path('publicacion/comentario/editar/<uuid:comentario_id>/', editar_comentario),
    path('publicacion/comentario/eliminar/<uuid:comentario_id>/', eliminar_comentario),





]