from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_article_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='test',
        ),
    ]
