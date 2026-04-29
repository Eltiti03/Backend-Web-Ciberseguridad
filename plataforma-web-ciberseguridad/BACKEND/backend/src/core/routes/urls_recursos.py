from ..controllers.views_recursos import crear_categoria_recurso, editar_categoria_recurso, eliminar_categoria_recurso, obtener_categorias_recurso, crear_recurso, editar_recurso, eliminar_recurso, obtener_recursos
from django.urls import path


urlpatterns = [
path('categoria/crear/', crear_categoria_recurso),
path('categoria/eliminar/<uuid:categoria_id>/', eliminar_categoria_recurso),
path('categoria/obtener/all/', obtener_categorias_recurso),
path('categoria/recurso-edu/crear/', crear_recurso),
path('categoria/recurso-edu/editar/<uuid:recurso_id>/', editar_recurso),
path('categoria/recurso-edu/eliminar/<uuid:recurso_id>/', eliminar_recurso),
path('categoria/recurso-edu/obtener/all/', obtener_recursos),
path('categoria/editar/<uuid:categoria_id>/', editar_categoria_recurso)

]