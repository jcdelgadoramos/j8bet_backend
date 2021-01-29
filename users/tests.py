from django.test import RequestFactory, TestCase
from django.urls import reverse
from graphene import Schema
from graphene.test import Client
from users.factories import UserFactory
from users.graphql.schema import Mutation as UserMutation
from users.graphql.schema import Query as UserQuery

class QueryTest(TestCase):
    def setUp(self):
        self.basic_user = UserFactory()
        self.schema = Schema(query=UserQuery)
        super().setUp()

    def test_01_get_all_users(self):
        """
        This test evaluates retrieving all users.
        """

        query = """
            query getAllUsers {
                users: allUsers {
                    username
                }
            }
        """
        result = self.schema.execute(query)
        self.assertEqual(len(result.data["users"]), 1)
        self.assertEqual(
            self.basic_user.username, result.data["users"][0]["username"]
        )

    def test_02_get_single_user(self):
        """
        This test evalutes retrieving a single user.
        """

        query_by_id = """
            query getUserById {{
                user: userById(id: {id}) {{
                    id,
                    username,
                    email
                }}
            }}
        """.format(id=self.basic_user.id)
        result = self.schema.execute(query_by_id)
        self.assertEqual(
            self.basic_user.id, int(result.data["user"]["id"])
        )
        self.assertEqual(
            self.basic_user.username, result.data["user"]["username"]
        )
        query_by_username = """
            query getUserByUsername {{
                user: userByUsername(username: \"{username}\") {{
                    id,
                    username,
                    email
                }}
            }}
        """.format(username=self.basic_user.username)
        result = self.schema.execute(query_by_username)
        self.assertEqual(
            self.basic_user.id, int(result.data["user"]["id"])
        )
        self.assertEqual(
            self.basic_user.username, result.data["user"]["username"]
        )


class CreateAuthenticateUserMutationTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))
        self.schema = Schema(query=UserQuery, mutation=UserMutation)
        self.client = Client(self.schema)
        super().setUp()

    def test_01_create_user(self):
        """
        This test evaluates creating a User via mutation.
        """

        create_mutation = """
            mutation creatingANewUser(
                $username: String!,
                $email: String!,
                $password: String!
            ) {
                createUser (
                    username: $username,
                    email: $email,
                    password: $password
                ) {
                    user{
                        id,
                        username,
                        email,
                        password
                    }
                }
            }"""
        username = "username"
        password = "password"
        email = "user@j8.com"
        executed = self.client.execute(
            create_mutation,
            variables = dict(username=username, email=email, password=password), 
        )
        self.assertEqual(username, executed["data"]["createUser"]["user"]["username"])
        self.assertEqual(email, executed["data"]["createUser"]["user"]["email"])

    def test_02_login_user(self):
        """
        This test reproduces the whole login process for a user.
        """

        create_mutation = """
            mutation creatingANewUser(
                $username: String!,
                $email: String!,
                $password: String!
            ) {
                createUser (
                    username: $username,
                    email: $email,
                    password: $password
                ) {
                    user{
                        id,
                        username,
                        email,
                        password
                    }
                }
            }"""
        username = "username"
        password = "password"
        email = "user@j8.com"
        creation_response = self.client.execute(
            create_mutation,
            variables = dict(username=username, email=email, password=password), 
        )
        get_token_mutation = """
            mutation getTokenAuth($username: String!, $password: String!) {
                tokenAuth(username: $username, password: $password) {
                    token
                }
            }
        """
        token_response = self.client.execute(
            get_token_mutation,
            variables = dict(username=username, password=password),
        )
        self.assertIsNotNone(token_response["data"]["tokenAuth"]["token"])
