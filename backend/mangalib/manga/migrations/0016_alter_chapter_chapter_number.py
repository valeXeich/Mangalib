# Generated by Django 4.2.2 on 2023-07-04 10:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("manga", "0015_alter_chapter_chapter_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chapter",
            name="chapter_number",
            field=models.CharField(max_length=1000),
        ),
    ]
