# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-05 04:41
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0011_auto_20160804_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bytessignature',
            name='bytes4_signature',
            field=models.BinaryField(max_length=4, unique=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
        migrations.AlterField(
            model_name='bytessignature',
            name='hex_signature',
            field=models.CharField(max_length=8, unique=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
