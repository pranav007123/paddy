import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from paddy.models import user as PaddyUser
from shop.models import Category, Shop, Plant, Order, OrderItem, Complaint

def seed():
    print("Seeding data...")

    # 1. Create Admin User
    admin_email = "admin@paddy.com"
    try:
        admin = PaddyUser.objects.get(email=admin_email)
        print(f"Admin user already exists: {admin_email}")
    except PaddyUser.DoesNotExist:
        admin = PaddyUser(
            name="Admin User",
            email=admin_email,
            phone_number="1234567890",
            password="admin", # Plain text as per existing weird auth model
            confirm_password="admin",
            is_superuser=True
        )
        admin.save()
        print(f"Created Admin user: {admin_email} / admin")

    # 2. Create Categories
    categories = ['Indoor', 'Outdoor', 'Medicinal', 'Flowering', 'Succulents']
    db_categories = []
    for cat in categories:
        c, created = Category.objects.get_or_create(name=cat, defaults={'description': f'{cat} plants'})
        db_categories.append(c)
        if created:
            print(f"Created category: {cat}")

    # 3. Create Shop Owner & Shop
    shop_email = "shop@paddy.com"
    try:
        shop_user = PaddyUser.objects.get(email=shop_email)
    except PaddyUser.DoesNotExist:
        shop_user = PaddyUser(
            name="Green Thumb",
            email=shop_email,
            phone_number="9876543210",
            password="shop",
            confirm_password="shop",
            is_superuser=False
        )
        shop_user.save()
        print(f"Created Shop user: {shop_email} / shop")

    shop, created = Shop.objects.get_or_create(
        user=shop_user,
        defaults={
            'shop_name': "Green Thumb Nursery",
            'email': shop_email,
            'address': "123 Garden Lane",
            'description': "Best plants in town",
            'status': 'approved'
        }
    )
    if created:
        print("Created Shop: Green Thumb Nursery")

    # 4. Create Plants
    if shop.plants.count() == 0:
        for i in range(10):
            cat = random.choice(db_categories)
            plant = Plant.objects.create(
                shop=shop,
                name=f"{cat.name} Plant {i+1}",
                category=cat,
                description="A beautiful plant",
                price=Decimal(random.randint(100, 2000)),
                stock=random.randint(5, 50)
            )
            print(f"Created plant: {plant.name}")

    # 5. Create Customer & Orders
    user_email = "user@paddy.com"
    try:
        customer = PaddyUser.objects.get(email=user_email)
    except PaddyUser.DoesNotExist:
        customer = PaddyUser(
            name="Alice Customer",
            email=user_email,
            phone_number="5555555555",
            password="user",
            confirm_password="user",
            is_superuser=False
        )
        customer.save()
        print(f"Created Customer: {user_email} / user")

    # Create recent orders
    if Order.objects.count() < 5:
        for i in range(5):
            # Create order
            order = Order.objects.create(
                user=customer,
                total_amount=Decimal('0.00'), # Will calculate
                shipping_address="456 User St",
                order_status=random.choice(['pending', 'shipped', 'delivered'])
            )
            # Create items
            total = Decimal('0.00')
            for _ in range(random.randint(1, 4)):
                plant = random.choice(Plant.objects.all())
                qty = random.randint(1, 3)
                price = plant.price
                OrderItem.objects.create(
                    order=order,
                    plant=plant,
                    quantity=qty,
                    price=price
                )
                total += price * qty
            
            order.total_amount = total
            order.save()
            print(f"Created order #{order.id} for {total}")

    # 6. Create Complaint
    if Complaint.objects.count() == 0:
        Complaint.objects.create(
            user=customer,
            subject="Late Delivery",
            description="My plants arrived late.",
            is_resolved=False
        )
        print("Created dummy complaint")

    print("\n\nSEEDING COMPLETE.")
    print("------------------------------------------------")
    print("Use these credentials to login:")
    print(f"Admin: {admin_email} / admin")
    print(f"Shop:  {shop_email}  / shop")
    print("------------------------------------------------")

if __name__ == '__main__':
    seed()
