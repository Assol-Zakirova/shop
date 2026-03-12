from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True, default='-')
    price = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.title

STARS = ((i, '* ' * i) for i in range(1, 6))
class Review(models.Model):
    stars = models.IntegerField(choices=STARS, default=2)
    text = models.TextField(null=True, blank=True, default='-')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='review_set')
    def __str__(self):
        return self.text

class UserConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"