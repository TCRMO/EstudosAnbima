from django.urls import path

from . import views

app_name = 'simulados'

urlpatterns = [
    # Seleção de prova
    path('selecionar-prova/', views.selecionar_prova, name='selecionar_prova'),
    # Home / Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Simulado completo
    path('simulado/', views.lista_simulados, name='lista_simulados'),
    path(
        'simulado/<int:simulado_id>/iniciar/',
        views.iniciar_simulado,
        name='iniciar_simulado',
    ),
    # Por tema
    path('tema/', views.lista_temas, name='lista_temas'),
    path(
        'tema/<int:tema_id>/iniciar/',
        views.iniciar_tema,
        name='iniciar_tema',
    ),
    # Modo aleatório
    path('aleatorio/', views.iniciar_aleatorio, name='iniciar_aleatorio'),
    # Revisão de erros
    path('revisao/', views.iniciar_revisao, name='iniciar_revisao'),
    # Resolver questão (genérico para todas as modalidades)
    path(
        'tentativa/<int:tentativa_id>/questao/<int:indice>/',
        views.resolver_questao,
        name='resolver_questao',
    ),
    path(
        'tentativa/<int:tentativa_id>/resultado/',
        views.resultado,
        name='resultado',
    ),
    # Histórico
    path('historico/', views.historico, name='historico'),
    path(
        'tentativa/<int:tentativa_id>/detalhe/',
        views.detalhe_tentativa,
        name='detalhe_tentativa',
    ),
    # Reset de dados de estudo
    path('reset/', views.reset_dados, name='reset_dados'),
]
