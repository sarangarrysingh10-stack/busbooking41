from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(default='USA', max_length=50)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
            options={'verbose_name_plural': 'Cities', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_km', models.PositiveIntegerField(blank=True, null=True)),
                ('from_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departures', to='main.city')),
                ('to_city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arrivals', to='main.city')),
            ],
            options={'unique_together': {('from_city', 'to_city')}},
        ),
        migrations.CreateModel(
            name='BusTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_name', models.CharField(max_length=100)),
                ('bus_type', models.CharField(choices=[('AC', 'AC Sleeper'), ('NAC', 'Non-AC Sleeper'), ('SEATER', 'AC Seater'), ('LUXURY', 'Luxury')], default='AC', max_length=10)),
                ('departure_time', models.TimeField()),
                ('arrival_time', models.TimeField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('total_seats', models.PositiveIntegerField(default=40)),
                ('available_seats', models.PositiveIntegerField(default=40)),
                ('amenities', models.CharField(blank=True, max_length=255)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='main.route')),
            ],
            options={'ordering': ['departure_time']},
        ),
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('from_city', models.CharField(blank=True, max_length=100)),
                ('to_city', models.CharField(blank=True, max_length=100)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_resolved', models.BooleanField(default=False)),
            ],
            options={'verbose_name_plural': 'Inquiries', 'ordering': ['-created_at']},
        ),
    ]
