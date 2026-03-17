from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulados', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questao',
            name='url_imagem',
            field=models.URLField(blank=True, null=True),
        ),
    ]
