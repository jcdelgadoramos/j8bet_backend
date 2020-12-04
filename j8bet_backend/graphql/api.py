from graphene_federation import build_schema

from bets.graphql.schema import (
    Queries as BetsQueries,
    Mutations as BetsMutations,
)

class Queries(
    BetsQueries,
):
    pass


class Mutations (
    BetsMutations,
):
    pass

schema = build_schema(Queries, mutation=Mutations)