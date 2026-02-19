import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Tema',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('nome', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Temas',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Simulado',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('nome', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='Questao',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('numero', models.PositiveIntegerField()),
                ('codigo', models.CharField(max_length=20)),
                ('pergunta', models.TextField()),
                ('alternativa_a', models.TextField()),
                ('alternativa_b', models.TextField()),
                ('alternativa_c', models.TextField()),
                ('alternativa_d', models.TextField()),
                (
                    'resposta_correta',
                    models.CharField(
                        choices=[
                            ('A', 'A'),
                            ('B', 'B'),
                            ('C', 'C'),
                            ('D', 'D'),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    'simulado',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='questoes',
                        to='simulados.simulado',
                    ),
                ),
                (
                    'tema',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='questoes',
                        to='simulados.tema',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Questão',
                'verbose_name_plural': 'Questões',
                'ordering': ['simulado', 'numero'],
                'unique_together': {('simulado', 'numero')},
            },
        ),
        migrations.CreateModel(
            name='Tentativa',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'tipo',
                    models.CharField(
                        choices=[
                            ('simulado', 'Simulado Completo'),
                            ('tema', 'Por Tema'),
                            ('aleatorio', 'Aleatório'),
                            ('revisao', 'Revisão de Erros'),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    'data_inicio',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ('data_fim', models.DateTimeField(blank=True, null=True)),
                ('finalizada', models.BooleanField(default=False)),
                (
                    'simulado',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='tentativas',
                        to='simulados.simulado',
                    ),
                ),
                (
                    'tema',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='tentativas',
                        to='simulados.tema',
                    ),
                ),
            ],
            options={
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Resposta',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'resposta_escolhida',
                    models.CharField(
                        choices=[
                            ('A', 'A'),
                            ('B', 'B'),
                            ('C', 'C'),
                            ('D', 'D'),
                        ],
                        max_length=1,
                    ),
                ),
                ('correta', models.BooleanField()),
                (
                    'data_resposta',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'questao',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='respostas',
                        to='simulados.questao',
                    ),
                ),
                (
                    'tentativa',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='respostas',
                        to='simulados.tentativa',
                    ),
                ),
            ],
            options={
                'ordering': ['data_resposta'],
                'unique_together': {('tentativa', 'questao')},
            },
        ),
    ]
