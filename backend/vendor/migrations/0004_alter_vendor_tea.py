# Generated by Django 4.2.7 on 2023-11-28 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_alter_vendor_tea'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='tea',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor.tea'),
        ),
    ]
