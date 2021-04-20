from bets.graphql.mutations import (
    BetPlacementByEventMutation,
    BetPlacementByQuotaMutation,
    CreateAffairMutation,
    CreateEventMutation,
    CreateQuotaMutation,
    DeleteAffairMutation,
    DeleteEventMutation,
    DeleteQuotaMutation,
    UpdateAffairMutation,
    UpdateEventMutation,
    UpdateQuotaMutation,
)
from bets.graphql.queries import (
    AffairQuery,
    BetQuery,
    EventQuery,
    HelloQuery,
    PrizeQuery,
    QuotaQuery,
    TagQuery,
    TransactionQuery,
)
from graphene import ObjectType


class Queries(
    AffairQuery,
    BetQuery,
    EventQuery,
    PrizeQuery,
    QuotaQuery,
    TagQuery,
    TransactionQuery,
    HelloQuery,
):
    """
    Class joining all Queries from Bets application
    """

    pass


class Mutations(ObjectType):
    """
    Class joining all Mutations from Bets application
    """

    create_affair = CreateAffairMutation.Field()
    create_event = CreateEventMutation.Field()
    create_quota = CreateQuotaMutation.Field()
    update_affair = UpdateAffairMutation.Field()
    update_event = UpdateEventMutation.Field()
    update_quota = UpdateQuotaMutation.Field()
    delete_affair = DeleteAffairMutation.Field()
    delete_event = DeleteEventMutation.Field()
    delete_quota = DeleteQuotaMutation.Field()
    place_bet_by_event = BetPlacementByEventMutation.Field()
    place_bet_by_quota = BetPlacementByQuotaMutation.Field()
