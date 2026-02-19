import json

from django.conf import settings
from django.core.management.base import BaseCommand

from simulados.models import Questao, Simulado, Tema


class Command(BaseCommand):
    help = 'Importa questões do arquivo cfg_questoes.json para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            type=str,
            default='cfg_questoes.json',
            help='Caminho para o arquivo JSON (padrão: cfg_questoes.json)',
        )

    def handle(self, *args, **options):
        arquivo = settings.BASE_DIR / options['arquivo']

        self.stdout.write(f'Lendo arquivo: {arquivo}')

        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_questoes = 0

        for sim_data in data['simulados']:
            simulado, created = Simulado.objects.get_or_create(
                codigo=sim_data['id'],
                defaults={'nome': sim_data['nome']},
            )
            action = 'Criado' if created else 'Já existia'
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
