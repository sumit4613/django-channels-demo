from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class CreateDummyUserCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User(username="test_user")
        cls.user.set_password("test_password")
        cls.user.save()

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("create_dummy_user", *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()

    def test_dry_run(self):
        out = self.call_command("--dry_run")
        self.assertIn("You can create user with username: username='dummy'", out)

    def test_dry_run_with_username(self):
        out = self.call_command("--dry_run", "--username", "my_user")
        self.assertIn("You can create user with username: username='my_user'", out)

    def test_dry_run_with_already_existing_user(self):
        out = self.call_command("--dry_run", "--username", "test_user")
        self.assertIn("User username='test_user' already exists", out)

    def test_default_create_user(self):
        out = self.call_command()
        self.assertIn("User created with username: username='dummy' & password: password='dummy@123'", out)

    def test_default_create_user_errors_out_if_user_exists(self):
        self.call_command()
        second_time = self.call_command()
        self.assertIn("User with username: username='dummy' already exists", second_time)

    def test_create_user_with_username(self):
        out = self.call_command("--username", "my_user")
        self.assertIn("User created with username: username='my_user' & password: password='dummy@123'", out)

    def test_create_user_with_username_and_password(self):
        out = self.call_command("--username", "my_user", "--password", "my_password")
        self.assertIn("User created with username: username='my_user' & password: password='my_password'", out)