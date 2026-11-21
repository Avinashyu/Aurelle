from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'phone',
        'status',
        'created_at',
        'is_completed',
    )

    list_filter = (
        'status',
        'is_completed',
        'created_at',
    )

    search_fields = (
        'customer_name',
        'phone',
    )

    list_editable = (
        'status',
        'is_completed',
    )

    inlines = [OrderItemInline]


admin.site.register(OrderItem)