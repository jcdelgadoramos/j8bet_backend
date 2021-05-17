from bets.models import Affair, Bet, Event, Prize, Quota, Transaction
from django.forms import ModelForm


class AffairForm(ModelForm):
    """
    Form for Affair model
    """

    class Meta:
        model = Affair
        fields = (
            "manager",
            "description",
        )


class EventForm(ModelForm):
    """
    Form for Event model
    """

    class Meta:
        model = Event
        fields = (
            "manager",
            "affair",
            "name",
            "description",
            "rules",
            "expiration_date",
            "active",
            "completed",
        )


class TransactionForm(ModelForm):
    """
    Form for Transaction model
    """

    class Meta:
        model = Transaction
        fields = ("amount", "description")


class QuotaForm(ModelForm):
    """
    Form for Quota model
    """

    class Meta:
        model = Quota
        fields = (
            "manager",
            "event",
            "probability",
            "expiration_date",
            "active",
        )


class BetForm(ModelForm):
    """
    Form for Bet model
    """

    class Meta:
        model = Bet
        fields = (
            "transaction",
            "quota",
            "user",
            "potential_earnings",
            "won",
        )


class PrizeForm(ModelForm):
    """
    Form for Prize model
    """

    class Meta:
        model = Prize
        fields = ("bet", "user", "reward")
