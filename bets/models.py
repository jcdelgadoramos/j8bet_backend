from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """
    Class for Tag model.
    A Tag is a keyword/keyphrase which is used to classify affairs.
    """

    name = models.CharField("Nombre", max_length=255)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"


class Affair(models.Model):
    """
    Class for Affair model.
    An Affair is the general description of a situation on which
    Events are plausible to happen.
    """

    class Meta:
        verbose_name = "Asunto"
        verbose_name_plural = "Asuntos"

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrador",
        on_delete=models.CASCADE,
        related_name="affairs",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Etiquetas",
        related_name="affairs",
    )
    description = models.TextField("Descripción", null=False, blank=False)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )


class Event(models.Model):
    """
    Class for Event model.
    An Event is the specific situation proposed regarding an affair
    on which a bet will be placed.
    """

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrador",
        on_delete=models.CASCADE,
        related_name="events",
    )
    affair = models.ForeignKey(
        Affair,
        verbose_name="Situación",
        on_delete=models.CASCADE,
        related_name="events",
    )
    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", null=False, blank=False)
    rules = models.TextField("Reglas", null=True, blank=True)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )
    expiration_date = models.DateTimeField("Fecha de expiración")
    active = models.BooleanField("Activo", default=True)
    completed = models.BooleanField("Completado", null=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

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
        if self.active is False:
            self.quotas.update(active=False)
            super().save()
            return
        bets_to_update = list()
        if self.completed is True:
            prizes_to_create = list()
            for quota in self.quotas.all():
                for bet in quota.bets.filter(won=None):
                    # Reward amount calculation must include the
                    # probability-to-quota calculation. This should
                    # probably be done when creating a new quota
                    prize = Prize(
                        bet=bet,
                        user=bet.user,
                        reward=bet.quota.probability * bet.transaction.amount,
                    )
                    prizes_to_create.append(prize)
                    bet.won = True
                    bet.active = False
                    bets_to_update.append(bet)
            Prize.objects.bulk_create(prizes_to_create)
            self.expiration_date = timezone.now()
        elif self.completed is False:
            for quota in self.quotas.all():
                for bet in quota.bets.filter(won=None):
                    bet.won = False
                    bet.active = False
                    bets_to_update.append(bet)
            self.expiration_date = timezone.now()
        else:
            super().save()
            return
        Bet.objects.bulk_update(bets_to_update, fields=["won", "active"])
        self.quotas.update(active=False)
        self.active = False
        super().save()


class Transaction(models.Model):
    """
    Class for Transaction model.
    A Transaction is an action describing a money transference.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Apostador",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.DecimalField("Monto", max_digits=10, decimal_places=2)
    description = models.CharField("Descripción", max_length=255)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"

    def __str__(self):
        return str(self.amount)


class Quota(models.Model):
    """
    Class for Quota model.
    A Quota is a numeric value which describes the possibility of a certain
    Event of happening.
    """

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Administrador",
        on_delete=models.CASCADE,
        related_name="quotas",
    )
    event = models.ForeignKey(
        Event,
        verbose_name="Evento",
        on_delete=models.CASCADE,
        related_name="quotas",
    )
    probability = models.DecimalField(
        "Probabilidad",
        max_digits=6,
        decimal_places=5,
        validators=[MaxValueValidator(1), MinValueValidator(0)],
    )
    coeficient = models.DecimalField(
        "Coeficiente de ganancia",
        max_digits=9,
        decimal_places=5,
        default=1.00001,
        validators=[MinValueValidator(1)],
    )
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )
    expiration_date = models.DateTimeField("Fecha de expiración")
    active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"

    def __str__(self):
        return "{event} - {probability}".format(
            event=self.event, probability=self.probability
        )

    def calculate_coeficient(self):
        """
        Transforms a probability (numeric value from 0 to 1) into a
        coeficient which determines the potential earnings in bets.
        """
        # TODO implement the coeficient calculation
        # This calculation must not be part of the code, but instead be a
        # formula retrieved from .env, stored on database, or something else.

        self.coeficient = Decimal(1.00001)

    def save(self, **kwargs):
        """
        Function which saves a Quota model and deactivates previous ones
        """
        if self.active:
            self.event.quotas.update(active=False)
        self.calculate_coeficient()
        super().save()


class Bet(models.Model):
    """
    Class for Bet model.
    A Bet is the core of the whole system. It joins a Transaction for an amount
    of money to a Quota with a certain, weighted probability for a promise of a
    monetary reward which increases the amount being betted.
    """

    transaction = models.ForeignKey(
        Transaction,
        verbose_name="Transacción",
        on_delete=models.CASCADE,
        related_name="bets",
    )
    quota = models.ForeignKey(
        Quota,
        verbose_name="Cuota",
        on_delete=models.CASCADE,
        related_name="bets",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Apostador",
        on_delete=models.CASCADE,
        related_name="bets",
    )
    potential_earnings = models.DecimalField(
        "Ganancias potenciales", max_digits=12, decimal_places=2
    )
    won = models.BooleanField("Ganado", null=True)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)
    modification_date = models.DateTimeField(
        "Fecha de modificación", auto_now=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Apuesta"
        verbose_name_plural = "Apuestas"

    def __str__(self):
        return "{event} - {user} - {amount}".format(
            event=self.quota.event,
            user=self.user,
            amount=self.transaction.amount,
        )

    def save(self, **kwargs):
        """
        Function which prevents from saving a Bet with a disabled Quota.
        """
        if not self.quota.active:
            raise ValidationError(_("La cuota debe estar activa"))
        self.potential_earnings = (
            self.transaction.amount * self.quota.coeficient
        )
        self.won = None
        self.active = True
        super().save()


class Prize(models.Model):
    """
    Class for Prize model.
    A Prize is the reward for successfully completing a Bet.
    """

    bet = models.ForeignKey(
        Bet,
        verbose_name="Apuesta",
        on_delete=models.CASCADE,
        related_name="prizes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Apostador",
        on_delete=models.CASCADE,
        related_name="prizes",
    )
    reward = models.DecimalField("Ganancia", max_digits=12, decimal_places=2)
    creation_date = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Premio"
        verbose_name_plural = "Premios"

    def __str__(self):
        return "{event} - {user} - {amount}".format(
            event=self.bet.quota.event, user=self.user, amount=self.reward
        )
