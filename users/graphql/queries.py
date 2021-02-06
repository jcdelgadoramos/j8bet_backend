from django.contrib.auth import get_user_model
from graphene import Field, ID, List, ObjectType, String
from users.graphql.types import UserType
from graphql_jwt.decorators import login_required


class UserQuery(ObjectType):
    all_users = List(UserType)
    user_by_id = Field(UserType, id=ID())
    user_by_username = Field(UserType, username=String())

    @login_required
    def resolve_all_users(parent, info):
        return get_user_model().objects.all()

    @login_required
    def resolve_user_by_id(parent, info, id):
        return get_user_model().objects.get(id=id)

    @login_required
    def resolve_user_by_username(parent, info, username):
        return get_user_model().objects.get(username=username)
