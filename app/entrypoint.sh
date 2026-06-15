#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model  
from accounts.models import UserProfile
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    user = User.objects.create_superuser(email='admin@exemplo.com', password='admin123')
    UserProfile.objects.create(user=user, first_access_completed=True, created_by_admin=True)
    print('Admin user created')
else:
    print('Admin user already exists')
"

exec "$@"
