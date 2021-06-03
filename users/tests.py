from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from graphene import Node, Schema
from graphene.test import Client
from graphql_jwt.testcases import JSONWebTokenTestCase
from j8bet_backend.constants import BET_CONSUMER
from users.factories import UserFactory
from users.graphql.schema import Mutation as UserMutation
from users.graphql.schema import Query as UserQuery


class QueryTest(JSONWebTokenTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.bet_consumer_group = Group.objects.get(name=BET_CONSUMER)
        self.user = UserFactory.create(groups=(self.bet_consumer_group,))
        self.client.authenticate(self.user)
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
        result = self.client.execute(query)
        self.assertEqual(len(result.data["users"]), 2)
        self.assertIn(
            self.user.username,
            [user["username"] for user in result.data["users"]],
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
        """.format(
            id=self.user.id,
        )
        result = self.client.execute(query_by_id)
        self.assertEqual(
            self.user.id, int(Node.from_global_id(result.data["user"]["id"])[1])
        )
        self.assertEqual(self.user.username, result.data["user"]["username"])
        query_by_username = """
            query getUserByUsername {{
                user: userByUsername(username: \"{username}\") {{
                    id,
                    username,
                    email
                }}
            }}
        """.format(
            username=self.user.username,
        )
        result = self.client.execute(query_by_username)
        self.assertEqual(
            self.user.id, int(Node.from_global_id(result.data["user"]["id"])[1])
        )
        self.assertEqual(self.user.username, result.data["user"]["username"])

    def test_03_me(self):
        """
        This test evaluates the 'me' query.
        """

        query = """
            query {
                me {
                    username,
                    archived,
                    verified,
                    secondaryEmail,
                    groups {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertEqual(self.user.username, result.data["me"]["username"])
        self.assertEqual(
            self.user.status.archived, result.data["me"]["archived"]
        )
        self.assertEqual(
            self.user.status.verified, result.data["me"]["verified"]
        )
        self.assertEqual(
            self.user.status.secondary_email,
            result.data["me"]["secondaryEmail"],
        )
        self.assertEqual(
            self.user.groups.first().name,
            result.data["me"]["groups"]["edges"][0]["node"]["name"],
        )
        self.client.logout()
        result = self.client.execute(query)
        self.assertIsNone(result.data["me"])


class CreateUserMutationTest(TestCase):
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
            mutation creatingANewUser($input: CreateUserMutationInput!) {
                createUser (input: $input) {
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
            variables=dict(
                input=dict(username=username, email=email, password=password)
            ),
        )
        self.assertEqual(
            username,
            executed["data"]["createUser"]["user"]["username"],
        )
        self.assertEqual(email, executed["data"]["createUser"]["user"]["email"])
