# Generated by Django 4.2.2 on 2023-07-04 10:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("manga", "0014_alter_manga_backround_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chapter",
            name="chapter_number",
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
    ]