from django.db import models
from .category import Category
from django.urls import reverse

class Product(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilograms'),
        ('nos', 'Numbers'),
    )

    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, unique=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES, default='kg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('app:product_details',args=[self.category.slug,self.slug])
    def save(self, *args, **kwargs):
        # Check if stock is 0, and set is_available accordingly
        if self.stock == 0:
            self.is_available = False
        if self.stock>0:
            self.is_available = True
        
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

