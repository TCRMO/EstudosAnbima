from django.contrib import admin

from .models import Questao, Resposta, Simulado, Tema, Tentativa


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Simulado)
class SimuladoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'total_questoes']
    search_fields = ['nome']


@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'numero', 'simulado', 'tema', 'resposta_correta']
    list_filter = ['simulado', 'tema', 'resposta_correta']
    search_fields = ['pergunta', 'codigo']


@admin.register(Tentativa)
class TentativaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'simulado', 'tema', 'finalizada', 'data_inicio']
    list_filter = ['tipo', 'finalizada']


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ['tentativa', 'questao', 'resposta_escolhida', 'correta']
    list_filter = ['correta']
