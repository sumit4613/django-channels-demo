from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = """
        Create a dummy user
        python manage.py create_dummy_user
    """
    DEFAULT_USERNAME = "dummy"
    DEFAULT_PASSWORD = "dummy@123"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Username of the user",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password of the user, if not provided default password will be used",
        )
        parser.add_argument(
            "--dry_run",
            action="store_true",
            help="Use dry run to check if user exists or not",
        )

    def handle(self, *args, **options):
        username = options["username"] or self.DEFAULT_USERNAME
        if options["dry_run"]:
            self.check_user_exists(username)
            return

        password = options["password"] or self.DEFAULT_PASSWORD
        user = User(username=username)
        user.set_password(password)
        try:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User created with username: {username=} & password: {password=}"))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f"User with username: {username=} already exists"))

    def check_user_exists(self, username):
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User {username=} already exists"))
        else:
            self.stdout.write(self.style.SUCCESS(f"You can create user with username: {username=}"))
