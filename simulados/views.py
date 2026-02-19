from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Questao, Resposta, Simulado, Tema, Tentativa


def home(request):
    """Página inicial com overview e acesso rápido às funcionalidades."""
    total_questoes = Questao.objects.count()
    total_simulados = Simulado.objects.count()
    total_temas = Tema.objects.count()

    tentativas_finalizadas = Tentativa.objects.filter(finalizada=True)
    total_tentativas = tentativas_finalizadas.count()

    total_respostas = Resposta.objects.filter(
        tentativa__finalizada=True
    ).count()
    total_corretas = Resposta.objects.filter(
        tentativa__finalizada=True, correta=True
    ).count()
    percentual_geral = (
        round((total_corretas / total_respostas) * 100, 1)
        if total_respostas > 0
        else 0
    )

    # Últimas 5 tentativas
    ultimas_tentativas = tentativas_finalizadas[:5]

    context = {
        'total_questoes': total_questoes,
        'total_simulados': total_simulados,
        'total_temas': total_temas,
        'total_tentativas': total_tentativas,
        'total_respostas': total_respostas,
        'total_corretas': total_corretas,
        'percentual_geral': percentual_geral,
        'ultimas_tentativas': ultimas_tentativas,
    }
    return render(request, 'simulados/home.html', context)


def dashboard(request):
    """Dashboard detalhado de desempenho."""
    # Desempenho por tema
    temas = Tema.objects.all()
    desempenho_temas = []
    for tema in temas:
        respostas = Resposta.objects.filter(
            questao__tema=tema, tentativa__finalizada=True
        )
        total = respostas.count()
        corretas = respostas.filter(correta=True).count()
        percentual = round((corretas / total) * 100, 1) if total > 0 else 0
        desempenho_temas.append(
            {
                'tema': tema,
                'total': total,
                'corretas': corretas,
                'erradas': total - corretas,
                'percentual': percentual,
            }
        )
    desempenho_temas.sort(key=lambda x: x['percentual'])

    # Desempenho por simulado
    simulados = Simulado.objects.all()
    desempenho_simulados = []
    for simulado in simulados:
        tentativas = Tentativa.objects.filter(
            simulado=simulado, tipo='simulado', finalizada=True
        )
        if tentativas.exists():
            melhor = max(t.percentual_acerto for t in tentativas)
            ultima = tentativas.first()
            desempenho_simulados.append(
                {
                    'simulado': simulado,
                    'tentativas': tentativas.count(),
                    'melhor_nota': melhor,
                    'ultima_nota': ultima.percentual_acerto,
                }
            )
        else:
            desempenho_simulados.append(
                {
                    'simulado': simulado,
                    'tentativas': 0,
                    'melhor_nota': 0,
                    'ultima_nota': 0,
                }
            )

    # Questões mais erradas
    questoes_mais_erradas = (
        Questao.objects.annotate(
            total_respostas=Count('respostas', filter=Q(respostas__tentativa__finalizada=True)),
            total_erros=Count(
                'respostas',
                filter=Q(respostas__correta=False, respostas__tentativa__finalizada=True),
            ),
        )
        .filter(total_respostas__gt=0)
        .order_by('-total_erros')[:10]
    )

    context = {
        'desempenho_temas': desempenho_temas,
        'desempenho_simulados': desempenho_simulados,
        'questoes_mais_erradas': questoes_mais_erradas,
    }
    return render(request, 'simulados/dashboard.html', context)


# ── Simulado Completo ──────────────────────────────────────────────────


def lista_simulados(request):
    """Lista todos os simulados disponíveis."""
    simulados = Simulado.objects.all()
    simulados_info = []
    for s in simulados:
        tentativas = Tentativa.objects.filter(
            simulado=s, tipo='simulado', finalizada=True
        )
        melhor = (
            max(t.percentual_acerto for t in tentativas)
            if tentativas.exists()
            else None
        )
        simulados_info.append(
            {
                'simulado': s,
                'tentativas': tentativas.count(),
                'melhor_nota': melhor,
            }
        )
    return render(
        request,
        'simulados/lista_simulados.html',
        {'simulados_info': simulados_info},
    )


def iniciar_simulado(request, simulado_id):
    """Inicia uma tentativa de simulado completo."""
    simulado = get_object_or_404(Simulado, pk=simulado_id)
    tentativa = Tentativa.objects.create(tipo='simulado', simulado=simulado)
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Por Tema ───────────────────────────────────────────────────────────


def lista_temas(request):
    """Lista todos os temas disponíveis."""
    temas = Tema.objects.annotate(total_questoes=Count('questoes'))
    temas_info = []
    for t in temas:
        respostas = Resposta.objects.filter(
            questao__tema=t, tentativa__finalizada=True
        )
        total_resp = respostas.count()
        corretas = respostas.filter(correta=True).count()
        percentual = (
            round((corretas / total_resp) * 100, 1) if total_resp > 0 else None
        )
        temas_info.append(
            {
                'tema': t,
                'percentual': percentual,
            }
        )
    return render(
        request, 'simulados/lista_temas.html', {'temas_info': temas_info}
    )


def iniciar_tema(request, tema_id):
    """Inicia uma sessão de estudo por tema."""
    tema = get_object_or_404(Tema, pk=tema_id)
    tentativa = Tentativa.objects.create(tipo='tema', tema=tema)
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Modo Aleatório ─────────────────────────────────────────────────────


def iniciar_aleatorio(request):
    """Inicia modo aleatório com 20 questões de todos os temas."""
    tentativa = Tentativa.objects.create(tipo='aleatorio')
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Revisão de Erros ───────────────────────────────────────────────────


def iniciar_revisao(request):
    """Inicia revisão das questões mais erradas."""
    # Pega questões que o usuário já errou
    questoes_erradas_ids = (
        Resposta.objects.filter(correta=False, tentativa__finalizada=True)
        .values_list('questao_id', flat=True)
        .distinct()
    )

    if not questoes_erradas_ids:
        return render(request, 'simulados/sem_erros.html')

    tentativa = Tentativa.objects.create(tipo='revisao')
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Resolver Questão (genérico) ────────────────────────────────────────


def _get_questoes_tentativa(tentativa):
    """Retorna o queryset de questões para a tentativa."""
    if tentativa.tipo == 'simulado':
        return tentativa.simulado.questoes.all().order_by('numero')
    elif tentativa.tipo == 'tema':
        return Questao.objects.filter(tema=tentativa.tema).order_by('simulado__codigo', 'numero')
    elif tentativa.tipo == 'aleatorio':
        return Questao.objects.order_by('?')[:20]
    elif tentativa.tipo == 'revisao':
        ids_erradas = (
            Resposta.objects.filter(correta=False, tentativa__finalizada=True)
            .exclude(tentativa=tentativa)
            .values_list('questao_id', flat=True)
            .distinct()
        )
        return Questao.objects.filter(id__in=ids_erradas).order_by('?')[:20]
    return Questao.objects.none()


def resolver_questao(request, tentativa_id, indice):
    """View para resolver uma questão dentro de uma tentativa."""
    tentativa = get_object_or_404(Tentativa, pk=tentativa_id)

    if tentativa.finalizada:
        return redirect('simulados:resultado', tentativa_id=tentativa.id)

    questoes = list(_get_questoes_tentativa(tentativa))
    total_questoes = len(questoes)

    if indice >= total_questoes:
        # Finalizar tentativa
        tentativa.finalizada = True
        tentativa.data_fim = timezone.now()
        tentativa.save()
        return redirect('simulados:resultado', tentativa_id=tentativa.id)

    questao = questoes[indice]

    # Verificar se já respondeu esta questão
    resposta_existente = Resposta.objects.filter(
        tentativa=tentativa, questao=questao
    ).first()

    feedback = None
    if request.method == 'POST' and not resposta_existente:
        escolha = request.POST.get('resposta')
        if escolha in ['A', 'B', 'C', 'D']:
            resposta = Resposta.objects.create(
                tentativa=tentativa,
                questao=questao,
                resposta_escolhida=escolha,
                correta=(escolha == questao.resposta_correta),
            )
            feedback = {
                'escolha': escolha,
                'correta': resposta.correta,
                'resposta_certa': questao.resposta_correta,
            }
            resposta_existente = resposta

    elif resposta_existente:
        feedback = {
            'escolha': resposta_existente.resposta_escolhida,
            'correta': resposta_existente.correta,
            'resposta_certa': questao.resposta_correta,
        }

    # Progresso
    respondidas = tentativa.respostas.count()

    context = {
        'tentativa': tentativa,
        'questao': questao,
        'alternativas': questao.get_alternativas(),
        'indice': indice,
        'total_questoes': total_questoes,
        'progresso': round((respondidas / total_questoes) * 100)
        if total_questoes > 0
        else 0,
        'respondidas': respondidas,
        'feedback': feedback,
        'proximo_indice': indice + 1,
        'indice_anterior': indice - 1 if indice > 0 else None,
    }
    return render(request, 'simulados/resolver_questao.html', context)


# ── Resultado ──────────────────────────────────────────────────────────


def resultado(request, tentativa_id):
    """Mostra o resultado final de uma tentativa."""
    tentativa = get_object_or_404(Tentativa, pk=tentativa_id, finalizada=True)
    respostas = tentativa.respostas.select_related('questao', 'questao__tema').all()

    # Desempenho por tema nesta tentativa
    temas_dict = {}
    for resp in respostas:
        tema_nome = resp.questao.tema.nome
        if tema_nome not in temas_dict:
            temas_dict[tema_nome] = {'total': 0, 'corretas': 0}
        temas_dict[tema_nome]['total'] += 1
        if resp.correta:
            temas_dict[tema_nome]['corretas'] += 1

    desempenho_temas = []
    for tema_nome, dados in sorted(temas_dict.items()):
        percentual = round((dados['corretas'] / dados['total']) * 100, 1)
        desempenho_temas.append(
            {
                'nome': tema_nome,
                'total': dados['total'],
                'corretas': dados['corretas'],
                'erradas': dados['total'] - dados['corretas'],
                'percentual': percentual,
            }
        )

    context = {
        'tentativa': tentativa,
        'respostas': respostas,
        'desempenho_temas': desempenho_temas,
    }
    return render(request, 'simulados/resultado.html', context)


# ── Histórico ──────────────────────────────────────────────────────────


def historico(request):
    """Lista todas as tentativas finalizadas."""
    tentativas = Tentativa.objects.filter(finalizada=True)
    return render(
        request, 'simulados/historico.html', {'tentativas': tentativas}
    )


def detalhe_tentativa(request, tentativa_id):
    """Detalhe de uma tentativa com todas as respostas."""
    tentativa = get_object_or_404(Tentativa, pk=tentativa_id, finalizada=True)
    respostas = tentativa.respostas.select_related(
        'questao', 'questao__tema'
    ).all()
    return render(
        request,
        'simulados/detalhe_tentativa.html',
        {'tentativa': tentativa, 'respostas': respostas},
    )


def reset_dados(request):
    """Apaga todas as tentativas e respostas."""
    if request.method == 'POST':
        Tentativa.objects.all().delete()
        return redirect('simulados:home')
    return render(request, 'simulados/reset_confirmar.html')
