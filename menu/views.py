from django.shortcuts import render
from .models import FoodItem

def menu_list(request):
    foods = FoodItem.objects.filter(is_available=True)

    return render(request, 'home.html', {'foods': foods})
