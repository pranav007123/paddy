import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from shop.models import Category

# Desired categories
categories = [
    'Paddy',
    'Mango'
]

# Create or check existence
for name in categories:
    obj, created = Category.objects.get_or_create(name=name)
    if created:
        print(f'Created category: {name}')
    else:
        print(f'Category already exists: {name}')

# Cleanup others
count, _ = Category.objects.exclude(name__in=categories).delete()
if count > 0:
    print(f'Removed {count} other categories.')

print('Seeding complete. Current categories:')
for c in Category.objects.all():
    print(f'- {c.name}')
