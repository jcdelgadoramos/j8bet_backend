from bets.graphql.mutations import (
    BetPlacementByEventMutation,
    BetPlacementByQuotaMutation,
    CreateEventMutation,
    CreateQuotaMutation,
    DeleteEventMutation,
    DeleteQuotaMutation,
    UpdateEventMutation,
    UpdateQuotaMutation,
)
from bets.graphql.queries import (
    BetQuery,
    EventQuery,
    HelloQuery,
    PrizeQuery,
    QuotaQuery,
    TransactionQuery,
)
from graphene import ObjectType


class Queries(
    EventQuery, TransactionQuery, BetQuery, QuotaQuery, PrizeQuery, HelloQuery,
):
    """
    Class joining all Queries from Bets application
    """

    pass


class Mutations(ObjectType):
    """
    Class joining all Mutations from Bets application
    """

    create_event = CreateEventMutation.Field()
    create_quota = CreateQuotaMutation.Field()
    update_event = UpdateEventMutation.Field()
    update_quota = UpdateQuotaMutation.Field()
    delete_event = DeleteEventMutation.Field()
    delete_quota = DeleteQuotaMutation.Field()
    place_bet_by_event = BetPlacementByEventMutation.Field()
    place_bet_by_quota = BetPlacementByQuotaMutation.Field()
