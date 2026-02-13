from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from paddy.models import user as PaddyUser, fileupload  # Rename to avoid confusion
from django.db.models import Q
from .forms import * # You might need to check if forms.py needs migration too
from .decorators import admin_required
from django.conf import settings
import razorpay
import json
from decimal import Decimal

# --- Custom Auth Helper ---
def get_current_user(request):
    uid = request.session.get('uid')
    if uid:
        try:
            return PaddyUser.objects.get(id=uid)
        except PaddyUser.DoesNotExist:
            return None
    return None

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('uid'):
            return redirect('/login') # Redirect to paddy's login page
        return view_func(request, *args, **kwargs)
    return wrapper

# --- Admin Views ---

@admin_required
def admin_dashboard(request):
    shops = Shop.objects.all()
    users = PaddyUser.objects.all()
    categories = Category.objects.all()
    complaints = Complaint.objects.filter(is_resolved=False)
    orders = Order.objects.all()
    
    # Calculate Total Revenue
    total_revenue_val = sum(order.total_amount for order in orders)
    total_revenue = "{:.2f}".format(total_revenue_val)
    
    context = {
        'shops': shops,
        'users': users,
        'categories': categories,
        'complaints': complaints,
        'orders': orders, # Passed for recent orders list
        'orders_count': orders.count(),
        'total_revenue': total_revenue
    }
    return render(request, 'shop/admin_dashboard.html', context)

@admin_required
def view_shops(request):
    query = request.GET.get('q')
    if query:
        shops = Shop.objects.filter(
            Q(shop_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(user__name__icontains=query)
        ).order_by('-created_at')
    else:
        shops = Shop.objects.all().order_by('-created_at')

    # Status filtering for the tabbed view
    pending_shops = shops.filter(status='pending')
    approved_shops = shops.filter(status='approved')
    rejected_shops = shops.filter(status='rejected')

    context = {
        'shops': shops, # Keep this if needed for a general list
        'pending_shops': pending_shops,
        'approved_shops': approved_shops,
        'rejected_shops': rejected_shops,
        'search_query': query
    }
    return render(request, 'shop/admin_view_shops.html', context)

@admin_required
def approve_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    shop.status = 'approved'
    shop.save()
    messages.success(request, f'Shop "{shop.shop_name}" approved.')
    return redirect('view_shops')

@admin_required
def reject_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    shop.status = 'rejected'
    shop.save()
    messages.warning(request, f'Shop "{shop.shop_name}" rejected.')
    return redirect('view_shops')

@admin_required
def view_users(request):
    query = request.GET.get('q')
    
    # Exclude superusers from the list
    users = PaddyUser.objects.filter(is_superuser=False)
    
    if query:
        users = users.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )
    
    # Annotate users with 'is_shop_owner'
    for u in users:
        u.is_shop_owner = Shop.objects.filter(user=u).exists()
        
    return render(request, 'shop/admin_view_users.html', {'users': users, 'search_query': query})

@admin_required
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(PaddyUser, id=user_id)
        if user.is_superuser:
             messages.error(request, 'Cannot delete a superuser.')
        else:
            user.delete()
            messages.success(request, 'User deleted successfully.')
    return redirect('view_users')

@admin_required
def admin_view_all_orders(request):
    query = request.GET.get('q')
    orders = Order.objects.all().order_by('-created_at')
    
    if query:
        # Search by Order ID or User Name
        if query.isdigit():
            orders = orders.filter(id=query)
        else:
            orders = orders.filter(user__name__icontains=query)
            
    return render(request, 'shop/admin_view_all_orders.html', {'orders': orders, 'search_query': query})

@admin_required
def category_management(request):
    if request.method == 'POST':
        if 'add_category' in request.POST:
            name = request.POST.get('name')
            if name:
                Category.objects.get_or_create(name=name)
                messages.success(request, 'Category added.')
        elif 'delete_category' in request.POST:
            cat_id = request.POST.get('category_id')
            Category.objects.filter(id=cat_id).delete()
            messages.success(request, 'Category deleted.')
            
        return redirect('category_management')
        
    categories = Category.objects.all()
    return render(request, 'shop/admin_category_management.html', {'categories': categories})

@admin_required
def view_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'shop/admin_view_complaints.html', {'complaints': complaints})

@admin_required
def reply_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        complaint.admin_reply = reply
        complaint.is_resolved = True
        complaint.save()
        messages.success(request, 'Reply sent.')
        return redirect('view_complaints')
        
    return render(request, 'shop/admin_reply_complaint.html', {'complaint': complaint})

@admin_required
def view_reviews_admin(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'shop/admin_view_reviews.html', {'reviews': reviews})

@admin_required
def change_password_admin(request):
    current_user = get_current_user(request)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            current_user.password = new_password
            current_user.confirm_password = new_password
            current_user.save()
            messages.success(request, 'Password changed.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Passwords do not match.')
            
    return render(request, 'shop/admin_change_password.html')

@admin_required
def admin_predictions(request):
    # Fetch all uploads (predictions)
    uploads = fileupload.objects.all().order_by('-id') # Assuming new ones last, id desc
    
    # Optional: Enrich with user names if possible
    # This is inefficient (N+1 query equivalent manually), but acceptable for small scale
    for upload in uploads:
        try:
            u = PaddyUser.objects.get(id=upload.userid)
            upload.user_name = u.name
            upload.user_email = u.email
        except:
            upload.user_name = "Unknown User"
            upload.user_email = "-"
            
    return render(request, 'shop/admin_predictions.html', {'uploads': uploads})


# --- Adapted Views ---

# Note: Shop Login/Signup is handled by Paddy's main auth now (or we need to integrate it).
# For now, let's assume we use Paddy's existing users.
# Users who want to open a shop might need a separate registration or upgrade flow.
# Given the user wants to "integrate it", I'll expose the existing shop dashboard logic.

@login_required_custom
def shop_dashboard(request):
    current_user = get_current_user(request)
    if not current_user:
        return redirect('/login')

    # Check if this user has a shop
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        # If no shop, maybe redirect to shop registration?
        return redirect('shop_signup') 

    if shop.status != 'approved':
        messages.warning(request, f'Your shop status is: {shop.status}')
    
    plants = Plant.objects.filter(shop=shop)
    
    # Get orders for this shop's plants
    shop_plant_ids = Plant.objects.filter(shop=shop).values_list('id', flat=True)
    orders = Order.objects.filter(items__plant_id__in=shop_plant_ids).distinct()
    
    reviews = Review.objects.filter(shop=shop)
    
    context = {
        'shop': shop,
        'plants': plants,
        'bookings': orders, 
        'reviews': reviews,
    }
    return render(request, 'shop/shop_dashboard.html', context) # Namespace templates


def shop_signup(request):
    # Determine user from session
    current_user = get_current_user(request)
    if not current_user:
        return redirect('/login')
        
    if request.method == 'POST':
        # Adapting ShopRegistrationForm usage manually for now or migrate forms
        shop_name = request.POST.get('shop_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        description = request.POST.get('description')
        
        # Check if shop already exists for user
        if Shop.objects.filter(user=current_user).exists():
            messages.error(request, 'You already have a shop registered.')
            return redirect('shop_dashboard')

        shop = Shop(
            user=current_user,
            shop_name=shop_name,
            email=email,
            address=address,
            description=description,
            status='pending' 
        )
        shop.save()
        messages.success(request, 'Shop registration submitted successfully.')
        return redirect('shop_dashboard')

    return render(request, 'shop/shop_signup.html')


@login_required_custom
def plant_management(request):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
    
    # Prevent adding plants if shop is not approved
    if shop.status != 'approved':
        messages.warning(request, f'Your shop status is "{shop.status}". You can only add plants after admin approval.')
        return redirect('shop_dashboard')
    
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.shop = shop
            plant.save()
            messages.success(request, 'Plant added.')
            return redirect('plant_management')
    else:
        form = PlantForm()
    
    plants = Plant.objects.filter(shop=shop)
    
    context = {
        'form': form,
        'plants': plants,
    }
    return render(request, 'shop/shop_plant_management.html', context)


@login_required_custom
def edit_plant(request, plant_id):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
        plant = get_object_or_404(Plant, id=plant_id, shop=shop)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
        
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant updated successfully.')
            return redirect('plant_management')
    else:
        form = PlantForm(instance=plant)
    
    return render(request, 'shop/edit_plant.html', {'form': form, 'plant': plant})

@login_required_custom
def delete_plant(request, plant_id):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
        plant = get_object_or_404(Plant, id=plant_id, shop=shop)
        plant.delete()
        messages.success(request, 'Plant deleted successfully.')
    except (Shop.DoesNotExist, Plant.DoesNotExist):
        messages.error(request, 'Plant not found or access denied.')
    
    return redirect('plant_management')

# --- User Shopping Views ---

@login_required_custom
def user_shop_list(request):
    # List all approved shops
    shops = Shop.objects.filter(status='approved')
    return render(request, 'shop/user_view_shops.html', {'shops': shops})

@login_required_custom
def user_plant_list(request):
    plants = Plant.objects.filter(shop__status='approved')
    categories = Category.objects.all()
    context = {
        'plants': plants,
        'categories': categories
    }
    return render(request, 'shop/user_view_categories_plants.html', context)

@login_required_custom
def product_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    reviews = Review.objects.filter(plant=plant).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
    
    context = {
        'plant': plant,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'range_5': range(1, 6)
    }
    return render(request, 'shop/product_detail.html', context)

@login_required_custom
def add_to_cart(request, plant_id):
    current_user = get_current_user(request)
    plant = get_object_or_404(Plant, id=plant_id)
    
    # Prevent shop owner from buying their own product
    if plant.shop.user == current_user:
        messages.error(request, "You cannot purchase your own product.")
        return redirect('view_categories_plants')

    cart_item, created = Cart.objects.get_or_create(
        user=current_user,
        plant=plant,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, 'Added to cart')
    return redirect('view_cart')

@login_required_custom
def buy_now_single(request, plant_id):
    current_user = get_current_user(request)
    plant = get_object_or_404(Plant, id=plant_id)
    
    # Prevent shop owner from buying their own product
    if plant.shop.user == current_user:
        messages.error(request, "You cannot purchase your own product.")
        return redirect('view_categories_plants')

    # Add to cart (or update quantity)
    cart_item, created = Cart.objects.get_or_create(
        user=current_user,
        plant=plant,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    # Redirect directly to checkout
    return redirect('checkout')

from django.http import JsonResponse

@login_required_custom
def update_cart(request, item_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            cart_item = get_object_or_404(Cart, id=item_id, user=get_current_user(request))
            
            if quantity > 0:
                if quantity <= cart_item.plant.stock:
                    cart_item.quantity = quantity
                    cart_item.save()
                    msg = 'Cart updated'
                    status = 'success'
                else:
                    msg = f'Only {cart_item.plant.stock} available'
                    status = 'error'
            else:
                cart_item.delete()
                msg = 'Item removed'
                status = 'success'
                
            # If AJAX request, calculate and return new totals
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Recalculate totals
                current_user = get_current_user(request)
                cart_items = Cart.objects.filter(user=current_user)
                
                subtotal = sum(item.plant.price * item.quantity for item in cart_items)
                tax = subtotal * Decimal('0.05')
                delivery_charge = Decimal('40.00') if subtotal > 0 else Decimal('0.00')
                total_price = subtotal + tax + delivery_charge
                
                # Item specific total calculation if item still exists
                item_total = 0
                if quantity > 0 and status == 'success':
                     item_total = cart_item.plant.price * cart_item.quantity

                return JsonResponse({
                    'status': status,
                    'message': msg,
                    'item_total': item_total,
                    'subtotal': subtotal,
                    'tax': tax,
                    'delivery_charge': delivery_charge,
                    'total_price': total_price
                })

            if status == 'success':
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
                
        except ValueError:
            pass
    
    return redirect('view_cart')

@login_required_custom
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=get_current_user(request))
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('view_cart')

from decimal import Decimal

from django.db.models import F

@login_required_custom
def view_cart(request):
    current_user = get_current_user(request)
    # Annotate item_total for robust initial display
    cart_items = Cart.objects.filter(user=current_user).annotate(
        item_total=F('plant__price') * F('quantity')
    )
    
    subtotal = sum(item.plant.price * item.quantity for item in cart_items)
    tax = subtotal * Decimal('0.05')
    delivery_charge = Decimal('40.00') if subtotal > 0 else Decimal('0.00')
    total_price = subtotal + tax + delivery_charge
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_charge': delivery_charge,
        'total_price': total_price
    }
    
    return render(request, 'shop/user_view_cart.html', context)

@login_required_custom
def checkout(request):
    current_user = get_current_user(request)
    # Annotate item_total here too
    cart_items = Cart.objects.filter(user=current_user).annotate(
        item_total=F('plant__price') * F('quantity')
    )
    
    if not cart_items.exists():
        messages.error(request, 'Cart is empty')
        return redirect('view_cart')

    subtotal = sum(item.plant.price * item.quantity for item in cart_items)
    tax = subtotal * Decimal('0.05')
    delivery_charge = Decimal('40.00')
    total_price = subtotal + tax + delivery_charge
    
    # Create Razorpay Order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    data = { "amount": int(total_price * 100), "currency": "INR", "receipt": f"order_rcptid_{current_user.id}" }
    payment = client.order.create(data=data)
    
    if request.method == 'POST':
        address = request.POST.get('address')
        
        # Create Order
        order = Order.objects.create(
            user=current_user,
            total_amount=total_price,
            shipping_address=address,
            order_status='pending'
        )
        
        # Move cart items to order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                plant=item.plant,
                quantity=item.quantity,
                price=item.plant.price
            )
            # Reduce stock?
            if item.plant.stock >= item.quantity:
                item.plant.stock -= item.quantity
                item.plant.save()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('user_orders')
        
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_charge': delivery_charge,
        'total_price': total_price,
        'payment': payment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'shop/user_buy_now.html', context)

@login_required_custom
def user_orders(request):
    current_user = get_current_user(request)
    orders = Order.objects.filter(user=current_user).order_by('-created_at')
    return render(request, 'shop/user_view_previous_orders.html', {'orders': orders})

@login_required_custom
def order_receipt(request, order_id):
    current_user = get_current_user(request)
    order = get_object_or_404(Order, id=order_id, user=current_user)
    
    # Calculate breakdown
    subtotal = sum(item.total_price for item in order.items.all())
    tax = subtotal * Decimal('0.05')
    delivery = Decimal('40.00')
    
    context = {
        'order': order,
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery
    }
    return render(request, 'shop/order_receipt.html', context)


@login_required_custom
def shop_profile(request):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
    
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        description = request.POST.get('description')
        
        shop.shop_name = shop_name
        shop.contact_number = contact_number
        shop.address = address
        shop.description = description
        shop.save()
        messages.success(request, 'Profile updated')
        
    return render(request, 'shop/shop_profile.html', {'shop': shop})


@login_required_custom
def view_bookings(request):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')

    shop_plant_ids = Plant.objects.filter(shop=shop).values_list('id', flat=True)
    orders = Order.objects.filter(items__plant_id__in=shop_plant_ids).distinct()
    
    return render(request, 'shop/shop_view_bookings.html', {'bookings': orders})


@login_required_custom
def update_order_status(request, order_id, status):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
        
    order = get_object_or_404(Order, id=order_id)
    shop_plant_ids = Plant.objects.filter(shop=shop).values_list('id', flat=True)
    order_plant_ids = order.items.values_list('plant_id', flat=True)
    
    if any(pid in shop_plant_ids for pid in order_plant_ids):
        order.order_status = status
        order.save()
        messages.success(request, f'Order status updated to {status}')
    
    return redirect('view_bookings')
    
@login_required_custom
def view_reviews(request):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
        
    reviews = Review.objects.filter(shop=shop)
    return render(request, 'shop/shop_view_reviews.html', {'reviews': reviews})

@login_required_custom
def manage_shop_categories(request):
    current_user = get_current_user(request)
    try:
        shop = Shop.objects.get(user=current_user)
    except Shop.DoesNotExist:
        return redirect('shop_signup')
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name, defaults={'name': category_name})
            if created:
                messages.success(request, f'Category "{category_name}" created successfully')
            else:
                messages.warning(request, f'Category "{category_name}" already exists')
        else:
            messages.error(request, 'Category name is required')
        return redirect('manage_shop_categories')
    
    categories = Category.objects.all()
    return render(request, 'shop/shop_manage_categories.html', {'categories': categories})


@login_required_custom
def change_password_shop(request):
    current_user = get_current_user(request)
    if not current_user:
        return redirect('shop_signup')
        
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return render(request, 'shop/shop_change_password.html')
        
        if current_user.password != current_password:
            messages.error(request, 'Current password is incorrect')
            return render(request, 'shop/shop_change_password.html')
        
        current_user.password = new_password
        current_user.confirm_password = new_password # Update this one too just in case
        current_user.save()
        messages.success(request, 'Password changed successfully')
        return redirect('shop_dashboard')
    
    return render(request, 'shop/shop_change_password.html')

@login_required_custom
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        
        # Verify Signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client.utility.verify_payment_signature(params_dict)
            
            # Payment Successful
            current_user = get_current_user(request)
            
            # Retrieve cart items
            cart_items = Cart.objects.filter(user=current_user)
            subtotal = sum(item.plant.price * item.quantity for item in cart_items)
            tax = subtotal * Decimal('0.05')
            delivery_charge = Decimal('40.00')
            total_price = subtotal + tax + delivery_charge
            
            address = data.get('address', 'Address not provided')

            # Create Order
            order = Order.objects.create(
                user=current_user,
                total_amount=total_price,
                shipping_address=address,
                order_status='paid'
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    plant=item.plant,
                    quantity=item.quantity,
                    price=item.plant.price
                )
                if item.plant.stock >= item.quantity:
                    item.plant.stock -= item.quantity
                    item.plant.save()
            
            cart_items.delete()
            
            messages.success(request, 'Payment Successful! Order Placed.')
            return redirect('user_orders')

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment Verification Failed: Signature Mismatch')
            return redirect('view_cart')
            
    return redirect('view_cart')

@login_required_custom
def add_review(request, plant_id):
    if request.method == 'POST':
        plant = get_object_or_404(Plant, id=plant_id)
        current_user = get_current_user(request)
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Create or Update Review
        Review.objects.update_or_create(
            user=current_user,
            plant=plant,
            defaults={
                'review_type': 'plant',
                'rating': rating,
                'comment': comment,
                'shop': plant.shop
            }
        )
        messages.success(request, 'Review submitted successfully')
        return redirect('user_orders')
    
    return redirect('user_orders')
