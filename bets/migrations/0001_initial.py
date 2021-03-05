# Generated by Django 3.1.3 on 2021-03-05 01:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "potential_earnings",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        verbose_name="Ganancias potenciales",
                    ),
                ),
                ("won", models.BooleanField(null=True, verbose_name="Ganado")),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "modification_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Apuesta",
                "verbose_name_plural": "Apuestas",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Nombre"),
                ),
                ("description", models.TextField(verbose_name="Descripción")),
                (
                    "rules",
                    models.TextField(
                        blank=True, null=True, verbose_name="Reglas"
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "modification_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "expiration_date",
                    models.DateTimeField(verbose_name="Fecha de expiración"),
                ),
                (
                    "active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
                (
                    "completed",
                    models.BooleanField(null=True, verbose_name="Completado"),
                ),
            ],
            options={
                "verbose_name": "Evento",
                "verbose_name_plural": "Eventos",
            },
        ),
        migrations.CreateModel(
            name="Prize",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reward",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Ganancia"
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
            ],
            options={
                "verbose_name": "Premio",
                "verbose_name_plural": "Premios",
            },
        ),
        migrations.CreateModel(
            name="Quota",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "probability",
                    models.DecimalField(
                        decimal_places=5,
                        max_digits=6,
                        validators=[
                            django.core.validators.MaxValueValidator(1),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="Probabilidad",
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "modification_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "expiration_date",
                    models.DateTimeField(verbose_name="Fecha de expiración"),
                ),
                (
                    "active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
            ],
            options={"verbose_name": "Cuota", "verbose_name_plural": "Cuotas",},
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Monto"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=255, verbose_name="Descripción"
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "modification_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
            ],
            options={
                "verbose_name": "Transacción",
                "verbose_name_plural": "Transacciones",
            },
        ),
    ]
