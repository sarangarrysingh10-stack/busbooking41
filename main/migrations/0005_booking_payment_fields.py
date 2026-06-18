from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(choices=[('PAY_LATER', 'Pay Later / Counter'), ('PAYPAL', 'PayPal'), ('CARD', 'Debit / Credit Card'), ('NET_BANKING', 'Net Banking')], default='PAY_LATER', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('NOT_PAID', 'Not Paid'), ('PENDING', 'Payment Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')], default='NOT_PAID', max_length=12),
        ),
        migrations.AddField(
            model_name='booking',
            name='payer_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='booking',
            name='payer_upi_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_reference',
            field=models.CharField(blank=True, help_text='PayPal/Card/Net Banking transaction reference ID', max_length=100),
        ),
    ]
