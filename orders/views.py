from django.shortcuts import redirect, render, get_object_or_404
from menu.models import FoodItem
from .models import Order, OrderItem


def add_to_cart(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    if not food.is_available:
        return redirect('home')

    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] += 1
    else:
        cart[food_id] = 1

    request.session['cart'] = cart
    return redirect('home')


def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart
    return redirect('cart')


def update_cart(request, food_id):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart[food_id] = quantity
        else:
            del cart[food_id]

    request.session['cart'] = cart
    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for food_id, quantity in cart.items():
        try:
            food = FoodItem.objects.get(id=food_id)
            subtotal = food.price * quantity
            total += subtotal

            cart_items.append({
                'food': food,
                'quantity': quantity,
                'subtotal': subtotal
            })

        except FoodItem.DoesNotExist:
            continue

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for food_id, quantity in cart.items():
        try:
            food = FoodItem.objects.get(id=food_id)

            if not food.is_available or not isinstance(quantity, int) or quantity <= 0:
                continue

            subtotal = food.price * quantity
            total += subtotal

            cart_items.append({
                'food': food,
                'quantity': quantity,
                'subtotal': subtotal
            })

        except (FoodItem.DoesNotExist, ValueError, TypeError):
            continue

    if not cart_items:
        return redirect('cart')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not customer_name or not phone or not address:
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'error': 'Please fill in all required fields.'
            })

        if not phone.isdigit() or len(phone) != 10:
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total': total,
                'error': 'Please enter a valid 10-digit phone number.'
            })

        order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            address=address
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                food=item['food'],
                quantity=item['quantity'],
                price=item['food'].price
            )

        request.session['cart'] = {}
        return redirect('order_success')

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

def order_success(request):
    return render(request, 'order_success.html')


def track_order(request):
    order = None
    error = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id', '').strip()
        phone = request.POST.get('phone', '').strip()

        try:
            order = Order.objects.get(
                id=order_id,
                phone=phone
            )
        except (Order.DoesNotExist, ValueError):
            error = "We couldn't find your order. Please check your details."

    return render(request, 'track_order.html', {
        'order': order,
        'error': error
    })


def update_order_status(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)

        new_status = request.POST.get('status')

        valid_statuses = ['Pending', 'Preparing', 'Ready', 'Delivered']

        if new_status in valid_statuses:
            order.status = new_status
            order.is_completed = (new_status == 'Delivered')
            order.save()

    return redirect('restaurant_dashboard')