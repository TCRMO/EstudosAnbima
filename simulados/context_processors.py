def prova_ativa(request):
    """Injeta a prova ativa da sessão em todos os templates."""
    return {'prova_ativa': request.session.get('prova')}
