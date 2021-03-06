# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-02 19:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exch_balance_enabled', models.BooleanField()),
                ('exch_code', models.CharField(max_length=10)),
                ('exch_fee', models.DecimalField(decimal_places=6, max_digits=14)),
                ('exch_id', models.IntegerField()),
                ('exch_name', models.CharField(max_length=80)),
                ('exch_trade_enabled', models.BooleanField()),
                ('exch_url', models.CharField(max_length=160)),
                ('is_user_enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mkt_id', models.IntegerField()),
                ('mkt_name', models.CharField(max_length=20)),
                ('exchmkt_id', models.IntegerField()),
                ('currency_one', models.CharField(blank=True, max_length=10, null=True)),
                ('currency_two', models.CharField(blank=True, max_length=10, null=True)),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='markets.Exchange')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='market',
            unique_together=set([('exchange', 'mkt_id')]),
        ),
    ]
