from django.contrib import admin

from .models import Payment,Order,OrderProduct

class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra=0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email','address_line_1','address_line_2','town', 'order_total', 'tax','delivery_fee', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered','is_delevered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20  # Align corrected
    inlines = [OrderProductInLine]

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment)

# Register your models here.
