from django.shortcuts import render
from django.contrib.auth.models import User
from users.models import CustomUser
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
from django.shortcuts import get_object_or_404
from common.validators import ageValidator
from rest_framework import generics
from product.serializers import CustomTokenObtainPairSerializer
from common.permissions import IsOwner, IsAnonymous, CanEditWithin15Minutes, IsModerator
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CategoriesListApiView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("product"))

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryValidateSerializer
        return CategoryListSerializer
class CategoriesDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CategoryValidateSerializer
        return CategoryDetailSerializer

class ProductsListApiView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAnonymous | IsModerator]
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductValidateSerializer
        return ProductListSerializer
     
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionError("Authentication required to create a product.")
        
        ageValidator(self.request)

        category_name = self.request.data.get('category_name')

        category, _ = Category.objects.get_or_create(name=category_name)
        owner_id = None
    
        if self.request.auth:
            owner_id = self.request.auth.get('user_id')

        if not owner_id and self.request.user and self.request.user.is_authenticated:
            owner_id = self.request.user.id

        owner = CustomUser.objects.filter(id=owner_id).first() if owner_id else None
        with transaction.atomic():
            serializer.save(category=category, owner=owner)
            
class ProductsDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAnonymous | (IsOwner & CanEditWithin15Minutes) | IsModerator]
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductValidateSerializer
        return ProductDetailSerializer

    def perform_update(self, serializer):
        category_name = serializer.validated_data.get('category_name')
        category, _ = Category.objects.get_or_create(name=category_name)
        serializer.save(category=category)
        
class ReviewsListApiView(generics.ListCreateAPIView):
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewValidateSerializer
        return ReviewListSerializer

    def perform_create(self, serializer):
        product_name = serializer.validated_data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)

        serializer.save(product=product)
class ReviewsDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewValidateSerializer
        return ReviewDetailSerializer

    def perform_update(self, serializer):
        product_name = serializer.validated_data.get('product_name')
        product, _ = Product.objects.get_or_create(title=product_name)

        serializer.save(product=product)
    
class RegisterApiView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )

            code = generate_confirmation_code()

            UserConfirmation.objects.create(
                user=user,
                code=code
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "User created",
                "confirmation_code": code
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
        
class ConfirmUserApiView(generics.GenericAPIView):
    serializer_class = ConfirmUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        confirmation = UserConfirmation.objects.filter(user=user).first()
        if not confirmation:
            return Response({"error": "Confirmation code not found"}, status=404)

        if confirmation.code != code:
            return Response({"error": "Invalid code"}, status=400)

        user.is_active = True
        user.save(update_fields=['is_active'])

        confirmation.delete()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "User confirmed successfully",
                "token": token.key
            },
            status=status.HTTP_200_OK
        )
class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials or inactive user"},
                status=400
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Login successful",
                "token": token.key
            },
            status=status.HTTP_200_OK
        )
        