import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paddy.settings')
django.setup()

from shop.models import Category, Plant

def fix_categories():
    print("Resetting categories...")
    
    # Define wanted categories
    wanted_names = ['Paddy', 'Mango']
    
    # 1. Delete all other categories
    # Note: This will CASCADE delete all plants associated with deleted categories!
    # User said "not needed i add plantts", so deleting existing dummy plants is fine/desired.
    deleted_count, _ = Category.objects.exclude(name__in=wanted_names).delete()
    print(f"Deleted {deleted_count} unwanted categories (and associated plants).")

    # 2. Ensure allowed categories exist
    for name in wanted_names:
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': f'Products related to {name}'})
        if created:
            print(f"Created category: {name}")
        else:
            print(f"Category already exists: {name}")

    print("\nCURRENT CATEGORIES:")
    for c in Category.objects.all():
        print(f"- {c.name}")

if __name__ == '__main__':
    fix_categories()
