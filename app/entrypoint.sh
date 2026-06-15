#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model  
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email='admin@exemplo.com', password='admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

exec "$@"
