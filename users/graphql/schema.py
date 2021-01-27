from graphene import ObjectType
from graphql_jwt import ObtainJSONWebToken, Refresh, Verify
from users.graphql.queries import UserQuery


class Query(UserQuery):
    """
    Class joining all Queries from User application
    """

    pass


class Mutation(ObjectType):
    """
    Class joining all Mutations from User application and graphql_jwt
    """

    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
