from django.contrib.auth.models import User
from django.db import models

class Event(models.Model):
    """
    Class for Event model.
    An Event is the situation on which a bet will be placed.
    """

    description = models.TextField(null=False, blank=False)
    rules = models.TextField(null=True, blank=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modification_datetime = models.DateTimeField(auto_now=True)
    expiration_datetime = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


class Transaction(models.Model):
    """
    Class for Transaction model.
    A Transaction is an action describing a money transference.
    """

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    modification_datetime = models.DateTimeField(auto_now=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'


class Quota(models.Model):
    """
    Class for Quota model.
    A Quota is a numeric value which describes the possibility of a certain
    Event of happening.
    """

    event = models.ForeignKey(
        Event, verbose_name='event', on_delete=models.CASCADE)
    probability = models.DecimalField(max_digits=6, decimal_places=5)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modification_datetime = models.DateTimeField(auto_now=True)
    expiration_datetime = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'


class Bet(models.Model):
    """
    Class for Bet model.
    A Bet is the core of the whole system. It joins a Transaction for an amount
    of money to a Quota with a certain, weighted probability for a promise of a
    monetary reward which increases the amount being betted.
    """

    transaction = models.ForeignKey(
        Transaction, verbose_name='transaction', on_delete=models.CASCADE)
    quota = models.ForeignKey(
        Quota, verbose_name='quota', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name='user', on_delete=models.CASCADE)
    potential_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    won = models.BooleanField(null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modification_datetime = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'


class Prize(models.Model):
    """
    Class for Prize model.
    A Prize is the reward for successfully completing a Bet.
    """

    bet = models.ForeignKey(Bet, verbose_name='bet', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name='user', on_delete=models.CASCADE)
    reward = models.DecimalField(max_digits=12, decimal_places=2)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Premio'
        verbose_name_plural = 'Premios'