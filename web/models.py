from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image_path = models.CharField(max_length=255)  
    
    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # content = models.TextField()  <-- 移除這個
    
    # 收件資訊
    receiver_name = models.CharField(max_length=100, default='')
    receiver_phone = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=255, default='')

    # 付款資訊
    payment_name = models.CharField(max_length=100, default='')
    payment_phone = models.CharField(max_length=20, default='')
    account_last_5 = models.CharField(max_length=5, default='')

    total_price = models.IntegerField()
    shipping_fee = models.IntegerField(default=200)
    state = models.CharField(max_length=20, default='等待付款中')
    paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    gift_box = models.CharField(max_length=20, null=True, blank=True)
    paper_bag = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
