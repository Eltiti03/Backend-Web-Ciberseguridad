# src/core/routes/urls_usuarios.py
from django.urls import path
from ..controllers.views_usuarios import cambiar_password, editar_usuario, eliminar_usuario, health_check_view, logout, obtener_usuarios, obtener_usuarios_activos, registro_usuario, login, solicitar_codigo, verificar_codigo, me

urlpatterns = [
    path("health/", health_check_view),
    path("usuario/registro/", registro_usuario),
    path('usuario/solicitar-codigo/', solicitar_codigo),
    path("usuario/me/", me) ,
    path("usuario/logout/", logout),
    path('usuario/verificar/', verificar_codigo),
    path('usuario/cambiar-password/', cambiar_password),
    path("usuario/login/", login),
    path('usuario/delete/<uuid:usuario_id>/', eliminar_usuario),
    path('usuario/get/all/', obtener_usuarios),
    path('usuario/get/activos/', obtener_usuarios_activos),
    path('usuario/update/<uuid:usuario_id>/', editar_usuario),
]
