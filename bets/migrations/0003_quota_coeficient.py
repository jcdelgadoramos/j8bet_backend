# Generated by Django 3.1.3 on 2021-03-09 04:06

from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bets", "0002_auto_20210304_2039"),
    ]

    operations = [
        migrations.AddField(
            model_name="quota",
            name="coeficient",
            field=models.DecimalField(
                decimal_places=5,
                default=Decimal(
                    "1.000010000000000065512040237081237137317657470703125"
                ),
                max_digits=9,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Coeficiente de ganancia",
            ),
        ),
    ]
