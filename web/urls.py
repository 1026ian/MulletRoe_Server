from .views import index, orders, cart_add, cart_remove, cart_update_options, cart_detail, checkout, confirm_payment, admin_orders, admin_order_edit, admin_order_delete, admin_order_complete, about, contact, admin_products, admin_product_add, admin_product_edit, admin_product_delete
from django.urls import path

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path("orders/", orders, name="orders"),
    path("cart/add/<int:product_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", cart_remove, name="cart_remove"),
    path("cart/update_options/<int:product_id>/", cart_update_options, name="cart_update_options"),
    path("cart/", cart_detail, name="cart_detail"),
    path("checkout/", checkout, name="checkout"),
    path("orders/confirm/<int:order_id>/", confirm_payment, name="confirm_payment"),
    
    # 管理者頁面
    path("management/orders/", admin_orders, name="admin_orders"),
    path("management/orders/edit/<int:order_id>/", admin_order_edit, name="admin_order_edit"),
    path("management/orders/complete/<int:order_id>/", admin_order_complete, name="admin_order_complete"),
    path("management/orders/delete/<int:order_id>/", admin_order_delete, name="admin_order_delete"),
    
    path("management/products/", admin_products, name="admin_products"),
    path("management/products/add/", admin_product_add, name="admin_product_add"),
    path("management/products/edit/<int:product_id>/", admin_product_edit, name="admin_product_edit"),
    path("management/products/delete/<int:product_id>/", admin_product_delete, name="admin_product_delete"),
]