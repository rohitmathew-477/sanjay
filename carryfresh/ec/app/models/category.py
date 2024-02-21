from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    photo= models.ImageField(upload_to='images/categories/',null=True,blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural='categories'
    def get_url(self):
        return reverse('app:product_by_category',args=[self.slug])
    def __str__(self):
        return self.category_name 