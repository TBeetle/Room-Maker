# Generated by Django 5.0.1 on 2024-02-12 18:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app1", "0011_defaultstylesettings_door_color_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="convertedfile",
            name="image",
            field=models.CharField(
                default="/home/acmichelitch/TheBackyardigans/uploads/conversion_output/output.png",
                max_length=255,
            ),
        ),
    ]
