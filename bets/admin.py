from django.contrib import admin

from bets.models import Event, Transaction, Bet, Quota, Prize


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin class for Event model
    """

    pass
        

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin class for Transaction model
    """

    pass


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    """
    Admin class for Bet model
    """
    
    pass


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    """
    Admin class for Quota model
    """

    pass


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    """
    Admin class for Prize model
    """

    pass
