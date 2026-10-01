from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create a test user (if missing) and print its authentication token.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='testuser')
        parser.add_argument('--password', default='testpass123')

    def handle(self, *args, **opts):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=opts['username'])
        if created:
            user.set_password(opts['password'])
            user.save()
        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(
            f"User: {user.username} ({'created' if created else 'already existed'})"))
        self.stdout.write(self.style.SUCCESS(f'Token: {token.key}'))
        self.stdout.write(f'Header: Authorization: Token {token.key}')
