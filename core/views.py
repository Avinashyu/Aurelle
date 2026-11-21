from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from menu.models import FoodItem, Category
from orders.models import Order, OrderItem


# HOME PAGE
def home(request):
    foods = FoodItem.objects.filter(is_available=True)
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    if search_query:
        foods = foods.filter(name__icontains=search_query)

    if category_id:
        foods = foods.filter(category_id=category_id)

    return render(request, 'home.html', {
        'foods': foods,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    })

# ADMIN LOGIN
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('restaurant_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('restaurant_dashboard')

        return render(request, 'login.html', {
            'error': 'Invalid credentials or unauthorized account.'
        })

    return render(request, 'login.html')


# ADMIN LOGOUT
@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# RESTAURANT DASHBOARD
@login_required
def restaurant_dashboard(request):
    orders = Order.objects.prefetch_related(
        'items__food'
    ).order_by('-created_at')

    pending_count = Order.objects.filter(status='Pending').count()
    completed_count = Order.objects.filter(status='Delivered').count()

    revenue_data = OrderItem.objects.filter(
        order__status='Delivered'
    ).aggregate(
        revenue=Sum(
            ExpressionWrapper(
                F('price') * F('quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )

    total_revenue = revenue_data.get('revenue') or 0

    return render(request, 'dashboard.html', {
        'orders': orders,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'total_revenue': total_revenue,
    })


# MENU MANAGEMENT
@login_required
@never_cache
def manage_menu(request):
    foods = FoodItem.objects.all().order_by('name')

    return render(request, 'manage_menu.html', {
        'foods': foods
    })


# ADD FOOD
@login_required
@never_cache
def add_food(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '')
        image = request.POST.get('image', '').strip()
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'

        if not name or not description or not price or not category_id:
            return render(request, 'add_food.html', {
                'categories': categories,
                'error': 'Please fill in all required fields.'
            })

        try:
            category = Category.objects.get(id=category_id)

            FoodItem.objects.create(
                name=name,
                description=description,
                price=price,
                image=image,
                category=category,
                is_available=is_available
            )

            return redirect('manage_menu')

        except (Category.DoesNotExist, ValueError):
            return render(request, 'add_food.html', {
                'categories': categories,
                'error': 'Invalid category or price.'
            })

    return render(request, 'add_food.html', {
        'categories': categories
    })


# EDIT FOOD
@login_required
@never_cache
def edit_food(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '')
        image = request.POST.get('image', '').strip()
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'

        if not name or not description or not price or not category_id:
            return render(request, 'edit_food.html', {
                'food': food,
                'categories': categories,
                'error': 'Please fill in all required fields.'
            })

        try:
            category = Category.objects.get(id=category_id)

            food.name = name
            food.description = description
            food.price = price
            food.image = image
            food.category = category
            food.is_available = is_available
            food.save()

            return redirect('manage_menu')

        except (Category.DoesNotExist, ValueError):
            return render(request, 'edit_food.html', {
                'food': food,
                'categories': categories,
                'error': 'Invalid category or price.'
            })

    return render(request, 'edit_food.html', {
        'food': food,
        'categories': categories
    })


# DELETE FOOD
@login_required
@never_cache
def delete_food(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    if request.method == 'POST':
        food.delete()

    return redirect('manage_menu')


# QUICK AVAILABILITY TOGGLE
@login_required
@never_cache
def toggle_food(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    if request.method == 'POST':
        food.is_available = not food.is_available
        food.save()

    return redirect('manage_menu')


# UPDATE ORDER STATUS
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        valid_statuses = ['Pending', 'Preparing', 'Ready', 'Delivered']

        if status in valid_statuses:
            order.status = status
            order.save()

    return redirect('restaurant_dashboard')