from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_buslocation_driver_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='distance_km',
            new_name='distance_miles',
        ),
        migrations.RenameField(
            model_name='buslocation',
            old_name='speed_kmh',
            new_name='speed_mph',
        ),
    ]
