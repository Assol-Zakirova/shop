from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategoryListSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, ReviewListSerializer, ReviewDetailSerializer, ProductWithReviewsSerializer, ProductWithReviewsSerializer
from .models import Category, Product, Review
from django.db.models import Avg
from django.db.models import Count
# Create your views here.
@api_view(['GET'])
def categories_list_api_view(request):
    categories = Category.objects.annotate(products_count=Count("product"))
    data = CategoryListSerializer(categories, many=True).data
    return Response(
        data=data,
    )

@api_view(['GET'])
def categories_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = CategoryDetailSerializer(category, many=False).data
    return Response(data=data)


@api_view(['GET'])
def products_list_api_view(request):
    products = Product.objects.all()
    data = ProductListSerializer(products, many=True).data
    return Response(
        data=data,
    )


@api_view(['GET'])
def products_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = ProductDetailSerializer(product, many=False).data
    return Response(data=data)

@api_view(["GET"])
def reviews_list_api_view(request):
    reviews = Review.objects.all()
    data = ReviewListSerializer(reviews, many=True).data
    return Response(data)
@api_view(['GET'])
def reviews_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': 'category not found!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = ReviewDetailSerializer(review, many=False).data
    return Response(data=data)

@api_view(["GET"])
def products_reviews_list_api_view(request):
    products = Product.objects.prefetch_related("review_set").annotate(
        rating=Avg("review_set__stars")
    )
    data = ProductWithReviewsSerializer(products, many=True).data
    return Response(data)
