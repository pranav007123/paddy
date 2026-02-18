import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from paddy.models import user
from shop.models import Plant, Shop

try:
    seller = user.objects.get(email='seller@test.com')
    print(f"Found seller: {seller.email}")
    
    # Plants should cascade delete with shop/seller, but let's be explicit if needed
    count, _ = seller.delete()
    print(f"Deleted seller and {count-1} related objects.")

except user.DoesNotExist:
    print("Seller not found. Cleanup already done or not needed.")
