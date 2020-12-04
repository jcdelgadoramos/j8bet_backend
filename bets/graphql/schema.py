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
    EventMutation,
)


class Queries(
    EventQuery,
    TransactionQuery,
    BetQuery,
    QuotaQuery,
    PrizeQuery,
    HelloQuery,
):
    pass


class Mutations(ObjectType):
    create_event = EventMutation.Field()