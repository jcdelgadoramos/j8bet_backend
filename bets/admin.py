from django.contrib import admin

from bets.models import Event, Transaction, Bet, Quota, Prize
from bets.forms import EventForm, TransactionForm, BetForm, QuotaForm, PrizeForm


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin class for Event model
    """

    form = EventForm
    list_display = ('name', 'expiration_date', 'active', 'completed',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin class for Transaction model
    """

    form = TransactionForm


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    """
    Admin class for Bet model
    """
    
    form = BetForm
    list_display = ('user', 'quota', 'potential_earnings', 'active', 'won',)


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    """
    Admin class for Quota model
    """

    form = QuotaForm
    list_display = ('event', 'probability', 'creation_date', 'active',)


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    """
    Admin class for Prize model
    """

    form = PrizeForm
