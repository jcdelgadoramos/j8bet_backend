from django.contrib.auth import get_user_model
from graphene import Field, ID, List, ObjectType, String
from users.graphql.types import UserType


class UserQuery(ObjectType):
    all_users = List(UserType)
    user_by_id = Field(UserType, id=ID())
    user_by_username = Field(UserType, username=String())

    def resolve_all_users(parent, info):
        return get_user_model().objects.all()

    def resolve_user_by_id(parent, info, id):
        return get_user_model().objects.get(id=id)

    def resolve_user_by_username(parent, info, username):
        return get_user_model().objects.get(username=username)
