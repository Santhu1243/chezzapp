# Generated by Django 5.1.4 on 2025-02-04 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nonsap', '0026_incidentissue_resolutiondate_delete_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidentissue',
            name='priority',
            field=models.CharField(choices=[('P1', 'P1 - High'), ('P2', 'P2 - Medium'), ('P3', 'P3 - Low'), ('P4', 'P4 - Custom')], default='active', max_length=10),
        ),
    ]
