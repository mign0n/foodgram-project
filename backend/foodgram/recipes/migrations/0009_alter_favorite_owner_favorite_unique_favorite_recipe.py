# Generated by Django 4.2.2 on 2023-10-03 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0008_subscribe_unique_subscribe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owner',
                to=settings.AUTH_USER_MODEL,
                verbose_name='владелец списка избранных рецептов',
            ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=('owner', 'recipe'), name='unique_favorite_recipe'
            ),
        ),
    ]
