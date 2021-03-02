from graphene import ObjectType
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth.mutations import (
    ArchiveAccount,
    DeleteAccount,
    ObtainJSONWebToken,
    PasswordChange,
    PasswordReset,
    PasswordSet,
    RefreshToken,
    Register,
    RemoveSecondaryEmail,
    ResendActivationEmail,
    RevokeToken,
    SendPasswordResetEmail,
    SendSecondaryEmailActivation,
    SwapEmails,
    UpdateAccount,
    VerifyAccount,
    VerifySecondaryEmail,
    VerifyToken,
)
from users.graphql.queries import UserObjectQuery
from users.graphql.mutations import CreateUserMutation


class Query(MeQuery, UserObjectQuery, UserQuery):
    """
    Class joining all Queries from User application with UserQuery and MeQuery
    """

    pass


class Mutation(ObjectType):
    """
    Class joining all Mutations from User application and graphql_auth
    """

    create_user = CreateUserMutation.Field()
    register = Register.Field()
    verify_account = VerifyAccount.Field()
    resend_activation_email = ResendActivationEmail.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    password_reset = PasswordReset.Field()
    password_set = PasswordSet.Field()
    password_change = PasswordChange.Field()
    update_account = UpdateAccount.Field()
    archive_account = ArchiveAccount.Field()
    delete_account = DeleteAccount.Field()
    send_secondary_email_activation = SendSecondaryEmailActivation.Field()
    verify_secondary_email = VerifySecondaryEmail.Field()
    swap_emails = SwapEmails.Field()
    remove_secondary_email = RemoveSecondaryEmail.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = VerifyToken.Field()
    refresh_token = RefreshToken.Field()
    revoke_token = RevokeToken.Field()
