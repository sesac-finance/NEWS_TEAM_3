# Generated by Django 4.1.3 on 2022-12-08 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_recommend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TbRecommend',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('recommend', models.CharField(blank=True, max_length=16, null=True)),
            ],
            options={
                'db_table': 'tb_recommend',
                'managed': False,
            },
        ),
    ]
