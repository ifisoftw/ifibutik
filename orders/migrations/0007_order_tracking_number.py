# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Sipariş Takip Numarası'),
        ),
    ]
