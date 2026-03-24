from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Questao, Resposta, Simulado, Tema, Tentativa


# ── Helpers de prova ───────────────────────────────────────────────────


def _get_prova_ativa(request):
    """Retorna a prova armazenada na sessão ('CFG' ou 'CGA'), ou None."""
    return request.session.get('prova')


def _requer_prova(request):
    """Redireciona para seleção se nenhuma prova estiver ativa."""
    prova = _get_prova_ativa(request)
    if not prova:
        return redirect('simulados:selecionar_prova')
    return None


# ── Seleção de Prova ───────────────────────────────────────────────────


def selecionar_prova(request):
    """Tela inicial para o usuário escolher entre CFG e CGA."""
    if request.method == 'POST':
        prova = request.POST.get('prova')
        if prova in ['CFG', 'CGA']:
            request.session['prova'] = prova
            return redirect('simulados:home')

    context = {
        'cfg_simulados': Simulado.objects.filter(prova='CFG').count(),
        'cfg_questoes': Questao.objects.filter(simulado__prova='CFG').count(),
        'cga_simulados': Simulado.objects.filter(prova='CGA').count(),
        'cga_questoes': Questao.objects.filter(simulado__prova='CGA').count(),
    }
    return render(request, 'simulados/selecionar_prova.html', context)


# ── Home / Dashboard ───────────────────────────────────────────────────


def home(request):
    """Página inicial com overview e acesso rápido às funcionalidades."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    total_questoes = Questao.objects.filter(simulado__prova=prova).count()
    total_simulados = Simulado.objects.filter(prova=prova).count()
    total_temas = (
        Tema.objects.filter(questoes__simulado__prova=prova).distinct().count()
    )

    tentativas_finalizadas = Tentativa.objects.filter(finalizada=True, prova=prova)
    total_tentativas = tentativas_finalizadas.count()

    total_respostas = Resposta.objects.filter(
        tentativa__finalizada=True, tentativa__prova=prova
    ).count()
    total_corretas = Resposta.objects.filter(
        tentativa__finalizada=True, tentativa__prova=prova, correta=True
    ).count()
    percentual_geral = (
        round((total_corretas / total_respostas) * 100, 1)
        if total_respostas > 0
        else 0
    )

    ultimas_tentativas = tentativas_finalizadas[:5]

    context = {
        'prova': prova,
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
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    # Desempenho por tema (apenas da prova ativa)
    temas = Tema.objects.filter(questoes__simulado__prova=prova).distinct()
    desempenho_temas = []
    for tema in temas:
        respostas = Resposta.objects.filter(
            questao__tema=tema,
            tentativa__finalizada=True,
            tentativa__prova=prova,
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

    # Desempenho por simulado (apenas da prova ativa)
    simulados = Simulado.objects.filter(prova=prova)
    desempenho_simulados = []
    for simulado in simulados:
        tentativas = Tentativa.objects.filter(
            simulado=simulado, tipo='simulado', finalizada=True, prova=prova
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

    # Questões mais erradas (apenas da prova ativa)
    questoes_mais_erradas = (
        Questao.objects.filter(simulado__prova=prova)
        .annotate(
            total_respostas=Count(
                'respostas',
                filter=Q(
                    respostas__tentativa__finalizada=True,
                    respostas__tentativa__prova=prova,
                ),
            ),
            total_erros=Count(
                'respostas',
                filter=Q(
                    respostas__correta=False,
                    respostas__tentativa__finalizada=True,
                    respostas__tentativa__prova=prova,
                ),
            ),
        )
        .filter(total_respostas__gt=0)
        .order_by('-total_erros')[:10]
    )

    context = {
        'prova': prova,
        'desempenho_temas': desempenho_temas,
        'desempenho_simulados': desempenho_simulados,
        'questoes_mais_erradas': questoes_mais_erradas,
    }
    return render(request, 'simulados/dashboard.html', context)


# ── Simulado Completo ──────────────────────────────────────────────────


def lista_simulados(request):
    """Lista os simulados da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    simulados = Simulado.objects.filter(prova=prova)
    simulados_info = []
    for s in simulados:
        tentativas = Tentativa.objects.filter(
            simulado=s, tipo='simulado', finalizada=True, prova=prova
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
        {'simulados_info': simulados_info, 'prova': prova},
    )


def iniciar_simulado(request, simulado_id):
    """Inicia uma tentativa de simulado completo."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    simulado = get_object_or_404(Simulado, pk=simulado_id, prova=prova)
    tentativa = Tentativa.objects.create(
        tipo='simulado', simulado=simulado, prova=prova
    )
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Por Tema ───────────────────────────────────────────────────────────


def lista_temas(request):
    """Lista os temas da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    temas = (
        Tema.objects.filter(questoes__simulado__prova=prova)
        .distinct()
        .annotate(
            total_questoes=Count(
                'questoes', filter=Q(questoes__simulado__prova=prova)
            )
        )
    )
    temas_info = []
    for t in temas:
        respostas = Resposta.objects.filter(
            questao__tema=t,
            questao__simulado__prova=prova,
            tentativa__finalizada=True,
            tentativa__prova=prova,
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
        request,
        'simulados/lista_temas.html',
        {'temas_info': temas_info, 'prova': prova},
    )


def iniciar_tema(request, tema_id):
    """Inicia uma sessão de estudo por tema."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    tema = get_object_or_404(Tema, pk=tema_id)
    tentativa = Tentativa.objects.create(tipo='tema', tema=tema, prova=prova)
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Modo Aleatório ─────────────────────────────────────────────────────


def iniciar_aleatorio(request):
    """Inicia modo aleatório com 20 questões da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    ids = list(
        Questao.objects.filter(simulado__prova=prova)
        .order_by('?')[:20]
        .values_list('id', flat=True)
    )
    tentativa = Tentativa.objects.create(tipo='aleatorio', prova=prova, questoes_ids=ids)
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Revisão de Erros ───────────────────────────────────────────────────


def iniciar_revisao(request):
    """Inicia revisão das questões mais erradas da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    questoes_erradas_ids = (
        Resposta.objects.filter(
            correta=False,
            tentativa__finalizada=True,
            tentativa__prova=prova,
        )
        .values_list('questao_id', flat=True)
        .distinct()
    )

    if not questoes_erradas_ids:
        return render(request, 'simulados/sem_erros.html')

    ids = list(
        Questao.objects.filter(id__in=questoes_erradas_ids, simulado__prova=prova)
        .order_by('?')[:20]
        .values_list('id', flat=True)
    )
    tentativa = Tentativa.objects.create(tipo='revisao', prova=prova, questoes_ids=ids)
    return redirect('simulados:resolver_questao', tentativa_id=tentativa.id, indice=0)


# ── Resolver Questão (genérico) ────────────────────────────────────────


def _get_questoes_tentativa(tentativa):
    """Retorna a lista de questões para a tentativa."""
    prova = tentativa.prova
    if tentativa.tipo == 'simulado':
        return tentativa.simulado.questoes.all().order_by('numero')
    elif tentativa.tipo == 'tema':
        return (
            Questao.objects.filter(tema=tentativa.tema, simulado__prova=prova)
            .order_by('simulado__codigo', 'numero')
        )
    elif tentativa.tipo in ('aleatorio', 'revisao'):
        ids = tentativa.questoes_ids
        if ids:
            questoes_map = {q.id: q for q in Questao.objects.filter(id__in=ids)}
            return [questoes_map[qid] for qid in ids if qid in questoes_map]
        # Fallback para tentativas antigas sem IDs persistidos
        if tentativa.tipo == 'aleatorio':
            return list(Questao.objects.filter(simulado__prova=prova).order_by('?')[:20])
        ids_erradas = (
            Resposta.objects.filter(
                correta=False,
                tentativa__finalizada=True,
                tentativa__prova=prova,
            )
            .exclude(tentativa=tentativa)
            .values_list('questao_id', flat=True)
            .distinct()
        )
        return list(
            Questao.objects.filter(id__in=ids_erradas, simulado__prova=prova)
            .order_by('?')[:20]
        )
    return Questao.objects.none()


def resolver_questao(request, tentativa_id, indice):
    """View para resolver uma questão dentro de uma tentativa."""
    tentativa = get_object_or_404(Tentativa, pk=tentativa_id)

    if tentativa.finalizada:
        return redirect('simulados:resultado', tentativa_id=tentativa.id)

    questoes = list(_get_questoes_tentativa(tentativa))
    total_questoes = len(questoes)

    if indice >= total_questoes:
        tentativa.finalizada = True
        tentativa.data_fim = timezone.now()
        tentativa.save()
        return redirect('simulados:resultado', tentativa_id=tentativa.id)

    questao = questoes[indice]

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
    """Lista tentativas finalizadas da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    tentativas = Tentativa.objects.filter(finalizada=True, prova=prova)
    return render(
        request,
        'simulados/historico.html',
        {'tentativas': tentativas, 'prova': prova},
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
    """Apaga todas as tentativas e respostas da prova ativa."""
    redir = _requer_prova(request)
    if redir:
        return redir
    prova = _get_prova_ativa(request)

    if request.method == 'POST':
        Tentativa.objects.filter(prova=prova).delete()
        return redirect('simulados:home')
    return render(request, 'simulados/reset_confirmar.html', {'prova': prova})
