from django.contrib.auth import get_user_model
from graphene import ID, Field, List, ObjectType, String
from users.graphql.types import UserType


class UserObjectQuery(ObjectType):
    all_users = List(UserType)
    me = Field(UserType)
    user_by_id = Field(UserType, id=ID())
    user_by_username = Field(UserType, username=String())

    def resolve_all_users(parent, info):
        return get_user_model().objects.all()

    def resolve_me(parent, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

    def resolve_user_by_id(parent, info, id):
        return get_user_model().objects.get(id=id)

    def resolve_user_by_username(parent, info, username):
        return get_user_model().objects.get(username=username)
