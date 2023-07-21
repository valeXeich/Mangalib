# Generated by Django 4.2.2 on 2023-06-17 12:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("manga", "0004_rename_anime_rating_manga"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(
                default="user/avatar/default.jpg", upload_to="user/avatars/"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="backround_image",
            field=models.ImageField(blank=True, upload_to="user/backgrounds/"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="dropped",
            field=models.ManyToManyField(
                blank=True, related_name="drops", to="manga.manga"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="favorite",
            field=models.ManyToManyField(
                blank=True, related_name="favorites", to="manga.manga"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="planned",
            field=models.ManyToManyField(
                blank=True, related_name="plans", to="manga.manga"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="readed",
            field=models.ManyToManyField(
                blank=True, related_name="read", to="manga.manga"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="reading",
            field=models.ManyToManyField(
                blank=True, related_name="readers", to="manga.manga"
            ),
        ),
    ]
