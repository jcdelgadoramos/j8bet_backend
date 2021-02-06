from graphene import ObjectType
from graphql_jwt import (
    DeleteJSONWebTokenCookie,
    DeleteRefreshTokenCookie,
    ObtainJSONWebToken,
    Refresh,
    Verify,
)
from users.graphql.queries import UserQuery
from users.graphql.mutations import CreateUser


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
    create_user = CreateUser.Field()
    delete_token_cookie = DeleteJSONWebTokenCookie.Field()
    delete_refresh_token_cookie = DeleteRefreshTokenCookie.Field()
