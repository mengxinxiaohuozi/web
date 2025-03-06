# Generated by Django 4.2 on 2025-03-05 15:11

from django.db import migrations, models
import loans.models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_alter_loanrecord_id_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanrecord',
            name='id_number',
            field=models.CharField(default='000000000000000000', max_length=18, verbose_name='身份证号'),
        ),
        migrations.AlterField(
            model_name='loanrecord',
            name='year',
            field=models.IntegerField(default=loans.models.get_current_year, verbose_name='年份'),
        ),
    ]
