# Generated by Django 5.0.6 on 2024-07-01 01:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("farm", "0002_alter_farm_farm_id_farmstatuslog"),
    ]

    operations = [
        migrations.AddField(
            model_name="farm",
            name="farm_name",
            field=models.CharField(default="Unknown", max_length=255),
        ),
        migrations.AddField(
            model_name="farm",
            name="farm_size",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]