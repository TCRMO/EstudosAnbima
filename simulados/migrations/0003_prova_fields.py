from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0002_questao_url_imagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulado',
            name='prova',
            field=models.CharField(
                choices=[('CFG', 'CFG'), ('CGA', 'CGA')],
                default='CFG',
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name='tentativa',
            name='prova',
            field=models.CharField(
                choices=[('CFG', 'CFG'), ('CGA', 'CGA')],
                default='CFG',
                max_length=3,
            ),
        ),
    ]
