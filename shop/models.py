from django.db import models
from paddy.models import user  # Importing existing custom user model

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Shop(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Using paddy.models.user instead of django.contrib.auth.models.User
    user = models.ForeignKey(user, on_delete=models.CASCADE) 
    shop_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name


class Plant(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='plants')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='plants/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('shop_owner', 'Shop Owner'), # Added shop_owner for clarity if needed
    ]
    
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.user_type}"


class Cart(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.plant.name}"

    @property
    def total_price(self):
        return self.plant.price * self.quantity


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.plant.name}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    service_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    booking_status = models.CharField(max_length=10, choices=BOOKING_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.name} at {self.shop.shop_name}"


class Complaint(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    reply = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint {self.subject} by {self.user.name}"


class Review(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('shop', 'Shop Review'),
        ('app', 'App Review'),
        ('plant', 'Plant Review'),
    ]
    
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, blank=True, null=True)
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPE_CHOICES)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.name}"
