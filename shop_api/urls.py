"""
URL configuration for shop_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from product.views import categories_list_api_view, categories_detail_api_view, products_list_api_view, products_detail_api_view, reviews_list_api_view, reviews_detail_api_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/categories/', categories_list_api_view),
    path('api/v1/categories/<int:id>/', categories_detail_api_view),
    path('api/v1/products/', products_list_api_view),
    path('api/v1/products/<int:id>/', products_detail_api_view),
    path('api/v1/reviews/', reviews_list_api_view),
    path('api/v1/reviews/<int:id>/', reviews_detail_api_view)
]
