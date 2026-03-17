from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategoryListSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, ReviewListSerializer, ReviewDetailSerializer, ProductWithReviewsSerializer, ProductWithReviewsSerializer, ProductValidateSerializer, CategoryValidateSerializer, ReviewValidateSerializer, RegisterSerializer, ConfirmUserSerializer, LoginSerializer
from .models import Category, Product, Review, UserConfirmation
from django.db.models import Avg
from django.db.models import Count
from django.db import transaction
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import random
from django.contrib.auth import authenticate

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
        serializer = CategoryValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        name = request.data.get('name')
        with transaction.atomic():       
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
        serializer = CategoryValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        price = serializer.validated_data.get('price')
        category_name = serializer.validated_data.get('category_name')
        category, _ = Category.objects.get_or_create(name=category_name) 
        with transaction.atomic():       
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
        serializer = ProductValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        serializer = ReviewValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)
        stars = request.data.get('stars')
        text = request.data.get('text')
        product_name = request.data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)
        with transaction.atomic():       
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
        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
def generate_confirmation_code():
    return str(random.randint(100000, 999999))


@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = User.objects.create_user(
        username=username,
        password=password,
        is_active=False
    )

    code = generate_confirmation_code()

    UserConfirmation.objects.create(
        user=user,
        code=code
    )

    return Response({
        "message": "User created",
        "confirmation_code": code
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def confirm_user_view(request):
    serializer = ConfirmUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    code = serializer.validated_data['code']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    try:
        confirmation = UserConfirmation.objects.get(user=user)
    except UserConfirmation.DoesNotExist:
        return Response({"error": "Confirmation code not found"}, status=404)

    if confirmation.code != code:
        return Response({"error": "Invalid code"}, status=400)

    user.is_active = True
    user.save()

    confirmation.delete()

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User confirmed successfully",
        "token": token.key
    })

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials or inactive user"},
            status=status.HTTP_400_BAD_REQUEST
        )

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Login successful",
        "token": token.key
    })

