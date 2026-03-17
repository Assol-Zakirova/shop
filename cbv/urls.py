from django.urls import path
from . views import CategoriesListApiView, ProductsListApiView, ProductsDetailApiView, ReviewsListApiView, ReviewsDetailApiView, ConfirmUserApiView, RegisterApiView, LoginApiView

urlpatterns = [
    path('categories/', CategoriesListApiView.as_view()),
    path('products/', ProductsListApiView.as_view()),
    path('products/<int:id>/', ProductsDetailApiView.as_view()),
    path('reviews/', ReviewsListApiView.as_view()),
    path('reviews/<int:id>/', ReviewsDetailApiView.as_view()),
    path('users/confirm/', ConfirmUserApiView.as_view()),
    path('users/register/', RegisterApiView.as_view()),
    path('users/login/', LoginApiView.as_view())

]