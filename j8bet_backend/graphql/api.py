from bets.graphql.schema import Mutations as BetsMutations
from bets.graphql.schema import Queries as BetsQueries
from users.graphql.schema import Mutation as UserMutations
from users.graphql.schema import Query as UserQueries
from graphene_federation import build_schema


class Query(BetsQueries, UserQueries,):
    pass


class Mutation(BetsMutations, UserMutations,):
    pass


schema = build_schema(Query, mutation=Mutation)
