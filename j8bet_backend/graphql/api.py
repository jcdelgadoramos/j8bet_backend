from bets.graphql.schema import Mutations as BetsMutations
from bets.graphql.schema import Queries as BetsQueries
from graphene_federation import build_schema


class Queries(BetsQueries,):
    pass


class Mutations(BetsMutations,):
    pass


schema = build_schema(Queries, mutation=Mutations)
