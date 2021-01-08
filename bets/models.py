from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class Event(models.Model):
    """
    Class for Event model.
    An Event is the situation on which a bet will be placed.
    """

    name = models.CharField('Nombre', max_length=255)
    description = models.TextField('Descripción', null=False, blank=False)
    rules = models.TextField('Reglas', null=True, blank=True)
    creation_date = models.DateTimeField(
        'Fecha de creación', auto_now_add=True)
    modification_date = models.DateTimeField(
        'Fecha de modificación', auto_now=True)
    expiration_date = models.DateTimeField('Fecha de expiración')
    active = models.BooleanField('Activo', default=True)
    completed = models.BooleanField('Completado', null=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        """
        Function which saves an Event and controls depending objects logic.
        """
        if not self.id:
            self.completed = None
            super().save()
            return
        if self.active == False:
            self.quotas.update(active=False)
            super().save()
            return
        bets_to_update = list()
        if self.completed == True:
            prizes_to_create = list()
            for quota in self.quotas.all():
                for bet in quota.bets.filter(won=None):
                    # Reward amount calculation must include the
                    # probability-to-quota calculation. This should
                    # probably be done when creating a new quota
                    prize = Prize(
                        bet=bet, user=bet.user,
                        reward=bet.quota.probability * bet.transaction.amount)
                    prizes_to_create.append(prize)
                    bet.won = True
                    bet.active = False
                    bets_to_update.append(bet)
            Prize.objects.bulk_create(prizes_to_create)
            self.expiration_date = datetime.now()
        elif self.completed == False:
            for quota in self.quotas.all():
                for bet in quota.bets.filter(won=None):
                    bet.won = False
                    bet.active = False
                    bets_to_update.append(bet)
            self.expiration_date = datetime.now()
        else:
            super().save()
            return
        Bet.objects.bulk_update(bets_to_update, fields=['won', 'active'])
        self.quotas.update(active=False)
        self.active = False
        super().save()
                

class Transaction(models.Model):
    """
    Class for Transaction model.
    A Transaction is an action describing a money transference.
    """

    amount = models.DecimalField('Monto', max_digits=10, decimal_places=2)
    description = models.CharField('Descripción', max_length=255)
    creation_date = models.DateTimeField(
        'Fecha de creación', auto_now_add=True)
    modification_date = models.DateTimeField(
        'Fecha de modificación', auto_now=True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return str(self.amount)


class Quota(models.Model):
    """
    Class for Quota model.
    A Quota is a numeric value which describes the possibility of a certain
    Event of happening.
    """

    event = models.ForeignKey(
        Event, verbose_name='Evento', on_delete=models.CASCADE,
        related_name='quotas')
    probability = models.DecimalField(
        'Probabilidad', max_digits=6, decimal_places=5, validators=[
            MaxValueValidator(1), MinValueValidator(0)])
    creation_date = models.DateTimeField(
        'Fecha de creación', auto_now_add=True)
    modification_date = models.DateTimeField(
        'Fecha de modificación', auto_now=True)
    expiration_date = models.DateTimeField('Fecha de expiración')
    active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'

    def __str__(self):
        return "{event} - {probability}".format(
            event=self.event, probability=self.probability) 

    def save(self, **kwargs):
        """
        Function which saves a Quota model and deactivates previous ones
        """
        if self.active:
            self.event.quotas.update(active=False)
        super().save()


class Bet(models.Model):
    """
    Class for Bet model.
    A Bet is the core of the whole system. It joins a Transaction for an amount
    of money to a Quota with a certain, weighted probability for a promise of a
    monetary reward which increases the amount being betted.
    """

    transaction = models.ForeignKey(
        Transaction, verbose_name='Transacción', on_delete=models.CASCADE,
        related_name='bets')
    quota = models.ForeignKey(
        Quota, verbose_name='Cuota', on_delete=models.CASCADE,
        related_name='bets')
    user = models.ForeignKey(
        User, verbose_name='Usuario', on_delete=models.CASCADE,
        related_name='bets')
    potential_earnings = models.DecimalField(
        'Ganancias potenciales', max_digits=12, decimal_places=2)
    won = models.BooleanField('Ganado', null=True)
    creation_date = models.DateTimeField(
        'Fecha de creación', auto_now_add=True)
    modification_date = models.DateTimeField(
        'Fecha de modificación', auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'

    def __str__(self):
        return "{event} - {user} - {amount}".format(
            event=self.quota.event, user=self.user, amount=self.transaction.amount) 

    def save(self, **kwargs):
        """
        Function which prevents from saving a Bet with a disabled Quota.
        """
        if not self.quota.active:
            raise ValidationError(_('La cuota debe estar activa'))
        self.won = None
        self.active = True
        super().save()


class Prize(models.Model):
    """
    Class for Prize model.
    A Prize is the reward for successfully completing a Bet.
    """

    bet = models.ForeignKey(
        Bet, verbose_name='Apuesta', on_delete=models.CASCADE,
        related_name='prizes')
    user = models.ForeignKey(
        User, verbose_name='Usuario', on_delete=models.CASCADE,
        related_name='prizes')
    reward = models.DecimalField('Ganancia', max_digits=12, decimal_places=2)
    creation_date = models.DateTimeField(
        'Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Premio'
        verbose_name_plural = 'Premios'

    def __str__(self):
        return "{event} - {user} - {amount}".format(
            event=self.bet.quota.event, user=self.user, amount=self.reward) 
