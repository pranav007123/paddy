from django.urls import path
from . import views

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/shops/', views.view_shops, name='view_shops'),
    path('admin/shops/approve/<int:shop_id>/', views.approve_shop, name='approve_shop'),
    path('admin/shops/reject/<int:shop_id>/', views.reject_shop, name='reject_shop'),
    path('admin/users/', views.view_users, name='view_users'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/orders/', views.admin_view_all_orders, name='admin_view_all_orders'),
    path('admin/categories/', views.category_management, name='category_management'),
    path('admin/complaints/', views.view_complaints, name='view_complaints'),
    path('admin/complaints/reply/<int:complaint_id>/', views.reply_complaint, name='reply_complaint'),
    path('admin/reviews/', views.view_reviews_admin, name='view_reviews_admin'),
    path('admin/change-password/', views.change_password_admin, name='change_password_admin'),
    path('admin/predictions/', views.admin_predictions, name='admin_predictions'),

    # Shop Owner URLs
    path('dashboard/', views.shop_dashboard, name='shop_dashboard'),
    path('signup/', views.shop_signup, name='shop_signup'),
    path('plants/', views.plant_management, name='plant_management'),
    path('plants/delete/<int:plant_id>/', views.delete_plant, name='delete_plant'),
    path('plants/edit/<int:plant_id>/', views.edit_plant, name='edit_plant'),
    path('profile/', views.shop_profile, name='shop_profile'),
    path('bookings/', views.view_bookings, name='view_bookings'),
    path('reviews/', views.view_reviews, name='view_reviews'),
    path('categories/', views.manage_shop_categories, name='manage_shop_categories'),
    path('change-password/', views.change_password_shop, name='change_password_shop'),
    path('order/status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    
    # User Shopping URLs
    path('catalog/', views.user_plant_list, name='view_categories_plants'),
    path('shops/', views.user_shop_list, name='user_shop_list'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:plant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy-now/<int:plant_id>/', views.buy_now_single, name='buy_now_single'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('product/<int:plant_id>/', views.product_detail, name='product_detail'),
    path('reviews/add/<int:plant_id>/', views.add_review, name='add_review'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders/receipt/<int:order_id>/', views.order_receipt, name='order_receipt'),
]
