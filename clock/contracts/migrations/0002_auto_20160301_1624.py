# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import clock.contracts.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='hours',
            field=clock.contracts.fields.WorkingHoursField(),
        ),
    ]
