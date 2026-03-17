import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from simulados.models import Questao, Simulado, Tema


class Command(BaseCommand):
    help = 'Importa questões de um arquivo JSON (cfg_questoes.json ou cga_questoes.json) para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            type=str,
            default='cfg_questoes.json',
            help='Caminho para o arquivo JSON (padrão: cfg_questoes.json)',
        )

    def handle(self, *args, **options):
        arquivo = settings.BASE_DIR / options['arquivo']

        # Derive the exam type and unique prefix from the filename
        # e.g. "cfg_questoes.json" → prova="CFG", prefix="CFG-"
        #      "cga_questoes.json" → prova="CGA", prefix="CGA-"
        basename = os.path.basename(options['arquivo'])
        prova = basename.replace('_questoes.json', '').upper()
        prefixo = prova + '-'

        self.stdout.write(f'Lendo arquivo: {arquivo}')
        self.stdout.write(f'Prova: {prova} | Prefixo de simulado: {prefixo}')

        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_questoes = 0

        for sim_data in data['simulados']:
            codigo_simulado = prefixo + sim_data['id']
            simulado, created = Simulado.objects.update_or_create(
                codigo=codigo_simulado,
                defaults={'nome': sim_data['nome'], 'prova': prova},
            )
            action = 'Criado' if created else 'Atualizado'
            self.stdout.write(f'  {action} simulado: {simulado.nome}')

            for q_data in sim_data['questoes']:
                tema, _ = Tema.objects.get_or_create(nome=q_data['tema'])

                _, q_created = Questao.objects.get_or_create(
                    simulado=simulado,
                    numero=q_data['numero'],
                    defaults={
                        'codigo': q_data['codigo'],
                        'pergunta': q_data['pergunta'],
                        'alternativa_a': q_data['alternativas']['A'],
                        'alternativa_b': q_data['alternativas']['B'],
                        'alternativa_c': q_data['alternativas']['C'],
                        'alternativa_d': q_data['alternativas']['D'],
                        'resposta_correta': q_data['resposta_correta'],
                        'tema': tema,
                        'url_imagem': q_data.get('url_imagem') or '',
                    },
                )
                if q_created:
                    total_questoes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nImportação concluída! {total_questoes} questões importadas.'
            )
        )
        self.stdout.write(
            f'Temas: {Tema.objects.count()} | '
            f'Simulados: {Simulado.objects.count()} | '
            f'Questões: {Questao.objects.count()}'
        )
