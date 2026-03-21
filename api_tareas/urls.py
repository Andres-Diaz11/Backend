from django.urls import path
from .views import TareaAPIView
from .views_auth import RegistroAPIView, LoginAPIView
from .views_perfil import PerfilImagenAPIView

urlpatterns = [
    # autenticación
    path('auth/registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),

    # tareas
    path('tareas/', TareaAPIView.as_view(), name='api_tareas'),  # listar y crear
    path('tareas/<str:tarea_id>/', TareaAPIView.as_view(), name='api_tarea_detalle'),  # ver, actualizar o eliminar por id

    # perfil
    path('perfil/foto/', PerfilImagenAPIView.as_view(), name='api_perfil_foto'),
    
]