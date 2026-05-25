# Generated migration for adding location field to Locality and making coordinates nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0002_localityprofile_infrastructure_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='locality',
            name='location',
            field=models.CharField(
                blank=True,
                help_text="Sector/Area/Landmark name (e.g., 'Sector 32', 'Downtown Area')",
                max_length=255,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='locality',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='locality',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True
            ),
        ),
    ]
