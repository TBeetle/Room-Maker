# Generated by Django 5.0.2 on 2024-03-10 04:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app1", "0018_alter_defaultstylesettings_font_color_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convertedfile",
            name="meta_location",
            field=models.TextField(default="Address", max_length=256),
        ),
    ]
