# Generated by Django 4.2.2 on 2023-06-16 11:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("manga", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rating",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ratings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="chapter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pages",
                to="manga.chapter",
            ),
        ),
        migrations.AddField(
            model_name="manga",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="manga",
                to="manga.author",
            ),
        ),
        migrations.AddField(
            model_name="manga",
            name="genres",
            field=models.ManyToManyField(to="manga.genres"),
        ),
        migrations.AddField(
            model_name="manga",
            name="painter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="manga",
                to="manga.painter",
            ),
        ),
        migrations.AddField(
            model_name="manga",
            name="publisher",
            field=models.ManyToManyField(related_name="manga", to="manga.publisher"),
        ),
        migrations.AddField(
            model_name="manga",
            name="related_manga",
            field=models.ManyToManyField(blank=True, to="manga.manga"),
        ),
        migrations.AddField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="manga",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="manga.manga",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="manga_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="manga.page",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="manga.comment",
            ),
        ),
        migrations.AddField(
            model_name="chapter",
            name="volume",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chapters",
                to="manga.volume",
            ),
        ),
    ]
