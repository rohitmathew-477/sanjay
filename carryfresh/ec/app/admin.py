from django.contrib import admin
from .models.category import Category
from .models.product import Product
from .models.slider import Slider

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('category_name',)}
    list_display=('category_name','slug')
admin.site.register(Category,CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available')
    list_filter = ['is_available']
    prepopulated_fields = {'slug':('product_name',)}
admin.site.register(Product,ProductAdmin)


    
admin.site.register(Slider)