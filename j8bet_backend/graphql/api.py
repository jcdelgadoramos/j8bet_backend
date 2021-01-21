from bets.graphql.schema import Mutations as BetsMutations
from bets.graphql.schema import Queries as BetsQueries
from graphene_federation import build_schema


class Query(BetsQueries,):
    pass


class Mutation(BetsMutations,):
    pass


schema = build_schema(Query, mutation=Mutation)
