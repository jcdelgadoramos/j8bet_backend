# Generated by Django 3.1.3 on 2021-03-05 01:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bets", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Apostador",
            ),
        ),
        migrations.AddField(
            model_name="quota",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="quotas",
                to="bets.event",
                verbose_name="Evento",
            ),
        ),
        migrations.AddField(
            model_name="quota",
            name="manager",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="quotas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Administrador",
            ),
        ),
        migrations.AddField(
            model_name="prize",
            name="bet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prizes",
                to="bets.bet",
                verbose_name="Apuesta",
            ),
        ),
        migrations.AddField(
            model_name="prize",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prizes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Apostador",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="manager",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Administrador",
            ),
        ),
        migrations.AddField(
            model_name="bet",
            name="quota",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bets",
                to="bets.quota",
                verbose_name="Cuota",
            ),
        ),
        migrations.AddField(
            model_name="bet",
            name="transaction",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bets",
                to="bets.transaction",
                verbose_name="Transacción",
            ),
        ),
        migrations.AddField(
            model_name="bet",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bets",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Apostador",
            ),
        ),
        migrations.AddField(
            model_name="affair",
            name="manager",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="affairs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Administrador",
            ),
        ),
        migrations.AddField(
            model_name="affair",
            name="tags",
            field=models.ManyToManyField(
                related_name="affairs",
                to="bets.Tag",
                verbose_name="Etiquetas",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="affair",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="bets.affair",
                verbose_name="Situación",
            ),
        ),
    ]
