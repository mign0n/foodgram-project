# Generated by Django 4.2.2 on 2023-10-10 12:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0003_alter_tag_color'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cart',
            name='unique_cart_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_recipe',
        ),
        migrations.RenameField(
            model_name='cart',
            old_name='owner',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='favorite',
            old_name='owner',
            new_name='author',
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(
                fields=('author', 'recipe'), name='unique_cart_recipe'
            ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=('author', 'recipe'), name='unique_favorite_recipe'
            ),
        ),
    ]
