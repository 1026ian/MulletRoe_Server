from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Product, Order, OrderItem

SHIPPING_FEE = 200

def index(request):
    if request.user.is_superuser:
        return redirect('admin_orders')
    products = Product.objects.all()
    return render(request, "index.html", {"products": products})

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_date')
    return render(request, "orders.html", {'orders': orders})

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

@login_required
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product_id)
    
    # 從 GET 參數取得數量，預設為 1
    qty = request.GET.get('qty', 1)
    try:
        qty = int(qty)
        if qty < 1: qty = 1
    except (ValueError, TypeError):
        qty = 1

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += qty
    else:
        cart[product_id_str] = {'quantity': qty, 'price': product.price}
    
    request.session['cart'] = cart
    return redirect('index')

@login_required
def cart_update_options(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        if product_id_str in cart:
            cart[product_id_str]['gift_box'] = request.POST.get('gift_box')
            cart[product_id_str]['paper_bag'] = request.POST.get('paper_bag')
            request.session['cart'] = cart
    return redirect('cart_detail')

@login_required
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0
    
    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = item['quantity'] * product.price
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'subtotal': subtotal,
            'gift_box': item.get('gift_box'),
            'paper_bag': item.get('paper_bag'),
        })
        grand_total += subtotal
        
    # 計算運費：超過 6000 免運
    current_shipping_fee = 0 if grand_total >= 6000 else SHIPPING_FEE
        
    return render(request, "cart.html", {
        'cart_items': cart_items, 
        'shipping_fee': current_shipping_fee,
        'grand_total': grand_total + current_shipping_fee,
        'item_total': grand_total
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')

    if request.method == 'POST':
        # 建立訂單
        receiver_name = request.POST.get('receiver_name')
        receiver_phone = request.POST.get('receiver_phone')
        address = request.POST.get('address')
        
        # 付款資訊
        payment_name = request.POST.get('payment_name')
        payment_phone = request.POST.get('payment_phone')
        account_last_5 = request.POST.get('account_last_5')
        
        # 計算總金額
        total_price = 0
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            total_price += item['quantity'] * product.price

        # 計算運費：超過 6000 免運
        current_shipping_fee = 0 if total_price >= 6000 else SHIPPING_FEE
            
        order = Order.objects.create(
            user=request.user,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            address=address,
            payment_name=payment_name,
            payment_phone=payment_phone,
            account_last_5=account_last_5,
            total_price=total_price + current_shipping_fee,
            shipping_fee=current_shipping_fee
        )
        
        # 建立訂單明細
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item['quantity'],
                gift_box=item.get('gift_box'),
                paper_bag=item.get('paper_bag')
            )
            
        # 清空購物車
        request.session['cart'] = {}
        return redirect('orders')
        
    else:
        # 顯示結帳頁面 (與 cart_detail 類似，需要計算金額給使用者看)
        cart_items = []
        grand_total = 0
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = int(item['quantity']) * product.price
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
                'gift_box': item.get('gift_box'),
                'paper_bag': item.get('paper_bag')
            })
            grand_total += subtotal
            
        # 計算運費：超過 6000 免運
        current_shipping_fee = 0 if grand_total >= 6000 else SHIPPING_FEE
            
        return render(request, "checkout.html", {
            'cart_items': cart_items, 
            'shipping_fee': current_shipping_fee,
            'grand_total': grand_total + current_shipping_fee,
            'item_total': grand_total
        })

@login_required
def confirm_payment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.state == '等待付款中':
            order.state = '等待賣家確認中'
            order.paid = True
            order.save()
    return redirect('orders')

@user_passes_test(lambda u: u.is_superuser)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_date')
    
    # 搜尋功能
    query = request.GET.get('q')
    if query:
        orders = orders.filter(
            Q(id__icontains=query) | 
            Q(receiver_name__icontains=query) |
            Q(user__username__icontains=query)
        )
        
    return render(request, "management/admin_orders.html", {'orders': orders, 'query': query})

@user_passes_test(lambda u: u.is_superuser)
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    states = ['等待付款中', '等待賣家確認中', '付款完成，盡快安排出貨', '已完成', '已取消']
    
    if request.method == 'POST':
        # 更新狀態與付款狀態
        order.state = request.POST.get('state')
        order.paid = request.POST.get('paid') == 'on'
        
        # 更新收件資訊
        order.receiver_name = request.POST.get('receiver_name')
        order.receiver_phone = request.POST.get('receiver_phone')
        order.address = request.POST.get('address')
        
        # 更新付款資訊
        order.payment_name = request.POST.get('payment_name')
        order.payment_phone = request.POST.get('payment_phone')
        order.account_last_5 = request.POST.get('account_last_5')
        
        order.save()
        return redirect('admin_orders')
        
    return render(request, "management/admin_order_edit.html", {'order': order, 'states': states})

@user_passes_test(lambda u: u.is_superuser)
def admin_order_complete(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.state = '已完成'
        order.save()
    return redirect('admin_orders')

@user_passes_test(lambda u: u.is_superuser)
def admin_order_delete(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.delete()
    return redirect('admin_orders')

@user_passes_test(lambda u: u.is_superuser)
def admin_products(request):
    products = Product.objects.all()
    return render(request, "management/admin_products.html", {'products': products})

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

@user_passes_test(lambda u: u.is_superuser)
def admin_product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image_file = request.FILES.get('image_file')
        
        image_path = "images/default_product.jpg" # 預設圖片
        
        if image_file:
            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/images/product'))
            filename = fs.save(image_file.name, image_file)
            image_path = f"images/product/{filename}"
            
        Product.objects.create(name=name, price=price, image_path=image_path)
        return redirect('admin_products')
    return render(request, "management/admin_product_form.html", {'title': '新增商品'})

@user_passes_test(lambda u: u.is_superuser)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        
        image_file = request.FILES.get('image_file')
        if image_file:
            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'static/images/product'))
            filename = fs.save(image_file.name, image_file)
            product.image_path = f"images/product/{filename}"
            
        product.save()
        return redirect('admin_products')
    return render(request, "management/admin_product_form.html", {'product': product, 'title': '編輯商品'})

@user_passes_test(lambda u: u.is_superuser)
def admin_product_delete(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('admin_products')
