from django.urls import path
from simulador import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/solicitudes/', views.SolicitudListCreateView.as_view(), name='api-solicitudes'),
]