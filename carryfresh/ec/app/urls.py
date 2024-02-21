from django.urls import include, path
from . import views
app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),  # This maps the root URL to the home view function
    path('about/', views.about, name='about'),
    
    
   
   
    path('all_products/', views.all_products, name='all_products'),
    path('all_products/<slug:category_slug>/', views.all_products, name='product_by_category'),
   path('all_products/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),

   path('search/',views.search,name='search'),
    
   
]
