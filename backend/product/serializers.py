from users.models import CustomUser
from rest_framework import serializers
from .models import Category, Product, Review
from django.contrib.auth.models import User
class CategoryListSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = 'name products_count'.split()

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = 'title price'.split()

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = 'text'.split()

class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewListSerializer(source="review_set", many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
class ProductValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, min_length=1, max_length=255)
    description = serializers.CharField(required=False, default='No text')
    price = serializers.IntegerField()
    category_name = serializers.CharField(write_only=True)

    def create(self, validated_data):
        validated_data.pop('category_name', None)
        return Product.objects.create(**validated_data)

class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

class ReviewValidateSerializer(serializers.Serializer):
    stars = serializers.IntegerField()
    text = serializers.CharField(required=False)
    product_name = serializers.CharField(write_only=True)
    def create(self, validated_data):
        validated_data.pop('product_name', None)
        return Review.objects.create(**validated_data)
class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")

        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("User already exists")

        return attrs
    
class ConfirmUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

