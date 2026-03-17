from django.db import models
from django.utils import timezone


class Tema(models.Model):
    nome = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Temas'

    def __str__(self):
        return self.nome


PROVA_CHOICES = [('CFG', 'CFG'), ('CGA', 'CGA')]


class Simulado(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=200)
    prova = models.CharField(max_length=3, choices=PROVA_CHOICES, default='CFG')

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return self.nome

    @property
    def total_questoes(self):
        return self.questoes.count()


class Questao(models.Model):
    simulado = models.ForeignKey(
        Simulado, on_delete=models.CASCADE, related_name='questoes'
    )
    tema = models.ForeignKey(
        Tema, on_delete=models.CASCADE, related_name='questoes'
    )
    numero = models.PositiveIntegerField()
    codigo = models.CharField(max_length=20)
    pergunta = models.TextField()
    alternativa_a = models.TextField()
    alternativa_b = models.TextField()
    alternativa_c = models.TextField()
    alternativa_d = models.TextField()
    resposta_correta = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    url_imagem = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['simulado', 'numero']
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        unique_together = ['simulado', 'numero']

    def __str__(self):
        return f"[{self.simulado.codigo}] Q{self.numero} - {self.codigo}"

    def get_alternativas(self):
        return [
            ('A', self.alternativa_a),
            ('B', self.alternativa_b),
            ('C', self.alternativa_c),
            ('D', self.alternativa_d),
        ]


class Tentativa(models.Model):
    """Representa uma sessão de estudo (simulado completo, por tema, etc.)."""

    TIPO_CHOICES = [
        ('simulado', 'Simulado Completo'),
        ('tema', 'Por Tema'),
        ('aleatorio', 'Aleatório'),
        ('revisao', 'Revisão de Erros'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prova = models.CharField(max_length=3, choices=PROVA_CHOICES, default='CFG')
    simulado = models.ForeignKey(
        Simulado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tentativas',
    )
    tema = models.ForeignKey(
        Tema,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tentativas',
    )
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    finalizada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_inicio']

    def __str__(self):
        label = self.get_tipo_display()
        if self.simulado:
            label += f" - {self.simulado.nome}"
        elif self.tema:
            label += f" - {self.tema.nome}"
        return label

    @property
    def total_questoes(self):
        return self.respostas.count()

    @property
    def total_corretas(self):
        return self.respostas.filter(correta=True).count()

    @property
    def total_erradas(self):
        return self.respostas.filter(correta=False).count()

    @property
    def percentual_acerto(self):
        total = self.total_questoes
        if total == 0:
            return 0
        return round((self.total_corretas / total) * 100, 1)


class Resposta(models.Model):
    tentativa = models.ForeignKey(
        Tentativa, on_delete=models.CASCADE, related_name='respostas'
    )
    questao = models.ForeignKey(
        Questao, on_delete=models.CASCADE, related_name='respostas'
    )
    resposta_escolhida = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    correta = models.BooleanField()
    data_resposta = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['data_resposta']
        unique_together = ['tentativa', 'questao']

    def __str__(self):
        status = "✓" if self.correta else "✗"
        return f"{status} {self.questao} - Resp: {self.resposta_escolhida}"

    def save(self, *args, **kwargs):
        self.correta = self.resposta_escolhida == self.questao.resposta_correta
        super().save(*args, **kwargs)
