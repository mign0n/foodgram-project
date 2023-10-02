# Generated by Django 4.2.2 on 2023-09-28 15:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0007_recipe_is_favorited_recipe_is_in_shopping_cart'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.UniqueConstraint(
                fields=('author', 'user'), name='unique_subscribe'
            ),
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.CheckConstraint(
                check=models.Q(('author', models.F('user')), _negated=True),
                name='author_is_not_user',
            ),
        ),
    ]