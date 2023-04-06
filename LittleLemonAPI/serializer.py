from rest_framework import serializers
from .models import *
from decimal import Decimal
from django.contrib.auth.models import User


#USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        extra_kwargs = {
            'password':{'write_only':True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

#class CategorySerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Category
#        fields = ['id', 'slug', 'title']


#MENU ITEM SERIALIZER
class MenuItemSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'feature', 'price_after_tax']

    def calculate_tax(self, product:MenuItem):
        return product.price * Decimal(1.1)



#CART SERIALIZER
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem']

class CartHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()

    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'price']

class CartAddSerializer(serializers.ModelSerializer):
    def validate_quantity(self, value):
        if(value < 2):
            raise serializers.ValidationError("Pls input your quantity")
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']



#ORDER SERIALIZER
class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']


class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer()

    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity']


class OrderPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew']

