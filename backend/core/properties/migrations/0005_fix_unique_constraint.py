from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_locality_location'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='locality',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='locality',
            constraint=models.UniqueConstraint(condition=models.Q(('latitude__isnull', False), ('longitude__isnull', False)), fields=('latitude', 'longitude'), name='unique_coordinates'),
        ),
    ]
