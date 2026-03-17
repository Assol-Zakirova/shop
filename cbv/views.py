from django.shortcuts import render
from django.contrib.auth.models import User
from product.views import generate_confirmation_code
from django.db import transaction
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Category, Product, Review, UserConfirmation
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from product.serializers import CategoryListSerializer, CategoryValidateSerializer, CategoryDetailSerializer, ProductListSerializer, ProductValidateSerializer, ProductDetailSerializer, ReviewListSerializer, ReviewDetailSerializer, ReviewValidateSerializer, RegisterSerializer, ConfirmUserSerializer, LoginSerializer


class CategoriesListApiView(APIView):
    def get(self, request):
        categories = Category.objects.annotate(products_count=Count("product"))
        data = CategoryListSerializer(categories, many=True).data
        return Response(data=data)

    def post(self, request):
        serializer = CategoryValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        name = serializer.validated_data.get("name")

        with transaction.atomic():
            category = Category.objects.create(name=name)

        return Response(
            status=status.HTTP_201_CREATED,
            data=CategoryDetailSerializer(category).data
        )
    
class CategoriesDetailApiView(APIView):
    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None

    def get(self, request, id):
        category = self.get_object(id)
        if category is None:
            return Response(
                data={'error': 'category not found!'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = CategoryDetailSerializer(category).data
        return Response(data=data)

    def put(self, request, id):
        category = self.get_object(id)
        if category is None:
            return Response(
                data={'error': 'category not found!'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category.name = serializer.validated_data.get('name')
        category.save()

        return Response(
            data=CategoryDetailSerializer(category).data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        category = self.get_object(id)
        if category is None:
            return Response(
                data={'error': 'category not found!'},
                status=status.HTTP_404_NOT_FOUND
            )

        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductsListApiView(APIView):
    def get(self, request):
        products = Product.objects.all()
        data = ProductListSerializer(products, many=True).data
        return Response(
            data=data,
        )
    def post(self, request):
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
class ProductsDetailApiView(APIView):
    def get_object(self, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    def get(self, id, request):
        product = self.get_object(id)
        if product is None:
            return Response(
                data={'error': 'product not found!'},
                status=status.HTTP_404_NOT_FOUND
            )
        data = ProductDetailSerializer(product, many=False).data
        return Response(data=data)
    def put(self, request, id):
        product = self.get_object(id)
        if product is None:
            return Response(
                data={'error': 'product not found!'},
                status=status.HTTP_404_NOT_FOUND
            )
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
    def delete(self, request, id):
        product = self.get_object(id)
        if product is None:
            return Response(
                data={'error': 'product not found!'},
                status=status.HTTP_404_NOT_FOUND
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ReviewsListApiView(APIView):
    def get(self, request):
        reviews = Review.objects.all()
        data = ReviewListSerializer(reviews, many=True).data
        return Response(data)

    def post(self, request):
        serializer = ReviewValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        stars = serializer.validated_data.get('stars')
        text = serializer.validated_data.get('text')
        product_name = serializer.validated_data.get('product_name')

        product, _ = Product.objects.get_or_create(title=product_name)

        with transaction.atomic():
            review = Review.objects.create(
                stars=stars,
                text=text,
                product=product
            )

        return Response(
            status=status.HTTP_201_CREATED,
            data=ReviewDetailSerializer(review).data
        )
class ReviewsDetailApiView(APIView):
    def get_object(self, id):
        try:
            return Review.objects.get(id=id)
        except Review.DoesNotExist:
            return None

    def get(self, request, id):
        review = self.get_object(id)
        if review is None:
            return Response(
                {"error": "review not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ReviewDetailSerializer(review).data)

    def put(self, request, id):
        review = self.get_object(id)
        if review is None:
            return Response(
                {"error": "review not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review.stars = serializer.validated_data.get('stars')
        review.text = serializer.validated_data.get('text')

        product_name = serializer.validated_data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)

        review.product = product   
        review.save()

        return Response(
            ReviewDetailSerializer(review).data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        review = self.get_object(id)
        if review is None:
            return Response(
                {"error": "review not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class RegisterApiView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        with transaction.atomic():
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

        return Response(
            {
                "message": "User created",
                "confirmation_code": code
            },                status=status.HTTP_201_CREATED
        )
        
class ConfirmUserApiView(APIView):
    def post(self, request):
        serializer = ConfirmUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            confirmation = UserConfirmation.objects.get(user=user)
        except UserConfirmation.DoesNotExist:
            return Response(
                {"error": "Confirmation code not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if confirmation.code != code:
            return Response(
                {"error": "Invalid code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = True
        user.save()

        confirmation.delete()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "User confirmed successfully",
                "token": token.key
            },
            status=status.HTTP_200_OK
        )
    
class LoginApiView(APIView):
    def post(self, request):
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

        return Response(
            {
                "message": "Login successful",
                "token": token.key
            },
            status=status.HTTP_200_OK
        )