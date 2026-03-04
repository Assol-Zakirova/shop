from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategoryListSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, ReviewListSerializer, ReviewDetailSerializer, ProductWithReviewsSerializer, ProductWithReviewsSerializer
from .models import Category, Product, Review
from django.db.models import Avg
from django.db.models import Count
# Create your views here.
@api_view(['GET', "POST"])
def categories_list_api_view(request):
    if request.method == 'GET':
        categories = Category.objects.annotate(products_count=Count("product"))
        data = CategoryListSerializer(categories, many=True).data
        return Response(
            data=data,
        )
    elif request.method == 'POST':
        name = request.data.get('name')
        category = Category.objects.create(name=name)

        return Response(status=status.HTTP_201_CREATED,
                        data=CategoryDetailSerializer(category).data)
@api_view(['GET', 'PUT', "DELETE"])
def categories_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = CategoryDetailSerializer(category, many=False).data
        return Response(data=data)
    elif request.method == "PUT":
        category.name = request.data.get('name')
        category.save()

        return Response(data=CategoryDetailSerializer(category).data,
                        status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET', 'POST'])
def products_list_api_view(request):
    if request.method == 'GET':
        products = Product.objects.all()
        data = ProductListSerializer(products, many=True).data
        return Response(
            data=data,
        )
    elif request.method == "POST":
        title = request.data.get('title')
        description = request.data.get('description')
        price = request.data.get('price')
        category_name = request.data.get('category_name')
        category, _ = Category.objects.get_or_create(name=category_name)        
        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            category=category
        )
        return Response(status=status.HTTP_201_CREATED,
                        data=ProductDetailSerializer(product).data)

@api_view(['GET', 'PUT', "DELETE"])
def products_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = ProductDetailSerializer(product, many=False).data
        return Response(data=data)
    elif request.method == 'PUT':
        product.title = request.data.get('title')
        product.description = request.data.get('description')
        product.price = request.data.get('price')
        category_name = request.data.get('category_name')
        category, _ = Category.objects.get_or_create(name=category_name)
        product.category = category
        product.save()
        return Response(data=ProductDetailSerializer(product).data,
                        status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(["GET", 'POST'])
def reviews_list_api_view(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        data = ReviewListSerializer(reviews, many=True).data
        return Response(data)
    elif request.method == 'POST':
        stars = request.data.get('stars')
        text = request.data.get('text')
        product_name = request.data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)
        review = Review.objects.create(
            stars=stars,
            text=text,
            product=product
        )

        return Response(status=status.HTTP_201_CREATED,
                        data=ReviewDetailSerializer(review).data)
@api_view(['GET', 'PUT', "DELETE"])
def reviews_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HcategoriesTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = ReviewDetailSerializer(review, many=False).data
        return Response(data=data)
    elif request.method == 'PUT':
        review.stars = request.data.get('stars')
        review.text = request.data.get('text')
        product_name = request.data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)
        review.save()
        return Response(data=ReviewDetailSerializer(review).data,
                        status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(["GET"])
def products_reviews_list_api_view(request):
    products = Product.objects.prefetch_related("review_set").annotate(
        rating=Avg("review_set__stars")
    )
    data = ProductWithReviewsSerializer(products, many=True).data
    return Response(data)
