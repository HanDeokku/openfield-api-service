# Generated by Django 5.0.6 on 2024-06-24 08:39

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Farm",
            fields=[
                (
                    "farm_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("farm_owner", models.CharField(max_length=255)),
                ("latitude", models.IntegerField()),
                ("longitude", models.IntegerField()),
            ],
        ),
    ]
