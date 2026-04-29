from django.core.management.base import BaseCommand, CommandError
from controller.models import CustomUser


class Command(BaseCommand):
    help = 'Create a new accounting user or promote an existing user to accounting access.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username for the accounting user')
        parser.add_argument('--password', type=str, required=False, help='Password (only for new users)')
        parser.add_argument('--email', type=str, required=False, default='', help='Email address')
        parser.add_argument('--promote', action='store_true', help='Promote an existing user instead of creating a new one')
        parser.add_argument('--demote', action='store_true', help='Remove accounting access from an existing user')

    def handle(self, *args, **options):
        username = options['username']
        promote = options['promote']
        demote = options['demote']

        if demote:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist.')

            user.is_accounting_user = False
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Accounting access REMOVED from user "{username}".'
            ))
            return

        if promote:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist.')

            if user.is_accounting_user:
                self.stdout.write(self.style.WARNING(
                    f'User "{username}" already has accounting access.'
                ))
                return

            user.is_accounting_user = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ User "{username}" promoted to accounting user.'
            ))
            return

        # Create new user
        password = options.get('password')
        if not password:
            raise CommandError('--password is required when creating a new user.')

        if CustomUser.objects.filter(username=username).exists():
            raise CommandError(
                f'User "{username}" already exists. Use --promote to grant accounting access.'
            )

        email = options.get('email', '')
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_accounting_user = True
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f'✓ Accounting user "{username}" created successfully.'
        ))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email or "(none)"}')
        self.stdout.write(f'  Accounting Access: Yes')
