from graphene import ObjectType

from bets.graphql.queries import (
    EventQuery,
    TransactionQuery,
    BetQuery,
    QuotaQuery,
    PrizeQuery,
    HelloQuery,
)

from bets.graphql.mutations import (
    CreateEventMutation,
    CreateQuotaMutation,
    UpdateEventMutation,
    UpdateQuotaMutation,
    DeleteEventMutation,
    DeleteQuotaMutation,
)


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
