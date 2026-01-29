import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from shop.models import Shop

shops = Shop.objects.filter(status='pending')
if shops.exists():
    for shop in shops:
        shop.status = 'approved'
        shop.save()
        print(f'Approved shop: {shop.shop_name}')
else:
    print('No pending shops found.')

# List all approved shops to confirm
print("\nCurrently Approved Shops:")
for shop in Shop.objects.filter(status='approved'):
    print(f"- {shop.shop_name}")
