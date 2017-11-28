# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shift_started', models.DateTimeField(verbose_name='Shift started')),
                ('shift_finished', models.DateTimeField(null=True, verbose_name='Shift finished')),
                ('shift_duration', models.DurationField(null=True, verbose_name='Shift duration', blank=True)),
                ('pause_started', models.DateTimeField(null=True, blank=True)),
                ('pause_duration', models.DurationField(default=datetime.timedelta(0), verbose_name='Pause duration')),
                ('note', models.TextField(verbose_name='Note', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contract', models.ForeignKey(blank=True, to='contracts.Contract', null=True)),
                ('employee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-shift_started'],
            },
        ),
    ]
