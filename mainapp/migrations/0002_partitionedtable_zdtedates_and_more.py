# Generated by Django 4.1.7 on 2023-04-28 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartitionedTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.TextField()),
                ('partition_name', models.TextField()),
            ],
            options={
                'db_table': 'pg_partitions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ZDTEDates',
            fields=[
                ('quote_datetime', models.DateField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'zdte_dates',
                'managed': False,
            },
        ),
        migrations.AlterModelTable(
            name='notionalgreeks',
            table='dev_spxw_data_p20210803',
        ),
    ]
