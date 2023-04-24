import math
from datetime import date

#DJANGO IMPORTS
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import *

#REST FRAMEWORK IMPORTS
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

#local file imports
from .models import MenuItem, Cart
from .serializer import *
from .throttles import TenCallsPerMinute


#LIST OF ALL USERS
@api_view(['GET', 'POST'])
@throttle_classes([TenCallsPerMinute])
def user(request):
   if request.method == 'GET':
      if request.user.groups.filter(name='Managers').exists():
         users = User.objects.all()
         serialized_item = UserSerializer(users, many=True)
         return Response(serialized_item.data, status.HTTP_200_OK)
      else:
         return Response({"message":"You are not authorized"}, status.HTTP_403_FORBIDDEN)
   if request.method == "POST":
      serialized_item = UserSerializer(data=request.data)
      serialized_item.is_valid(raise_exception=True)
      serialized_item.save()
      return Response(status.HTTP_201_CREATED)

#CURRENT USER
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def current_user(request):
   if request.method == 'GET':
      serialized_item = UserSerializer(request.user)
      return Response(serialized_item.data, status.HTTP_200_OK)


#MANAGERS GROUP
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([TenCallsPerMinute])
def managers(request):

   if request.method == 'GET':
      if request.user.groups.filter(name='Managers').exists() or request.user.groups.filter([IsAdminUser]):
         users = User.objects.filter(groups__name='Managers')
         serialized_item = UserSerializer(users, many=True)
         return Response(serialized_item.data, status.HTTP_200_OK)
      else:
         return Response({"message":"You are not authorized"}, status.HTTP_403_FORBIDDEN)

   username = request.data['username']
   if username:
      user = get_object_or_404(User, username=username)
      managers = Group.objects.get(name="Managers")

      if request.method == 'POST':
         managers.user_set.add(user)
         return Response({"message": "user added to the manager group"}, status.HTTP_201_CREATED)

      elif request.method == 'DELETE':
         managers.user_set.remove(user)
         return Response({"Success"}, status.HTTP_200_OK)

#DELIVERY CREW
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([TenCallsPerMinute])
def delivery_crew(request):

   if request.method == 'GET':
      if request.user.groups.filter(name='Managers').exists():
         users = User.objects.filter(groups__name='Delivery crew')
         serialized_item = UserSerializer(users, many=True)
         return Response(serialized_item.data, status.HTTP_200_OK)
      else:
         return Response({"message":"You are not authorized"}, status.HTTP_403_FORBIDDEN)

   username = request.data['username']
   if username:
      user = get_object_or_404(User, username=username)
      delivery_crew = Group.objects.get(name="Delivery crew")

      if request.method == 'POST':
         delivery_crew.user_set.add(user)
         return Response({"message": "user added to the delivery crew group"}, status.HTTP_201_CREATED)

      elif request.method == 'DELETE':
         delivery_crew.user_set.remove(user)
         return Response({"Success"}, status.HTTP_200_OK)


#CATEGORIES
@api_view(['GET', 'POST'])
def categories(request):
   if request.method == 'GET':
      if request.user.groups.filter(name='Managers').exists():
         items = Category.objects.all()
         serialized_item = CategorySerializer(items, many=True)
         return Response(serialized_item.data, status.HTTP_200_OK)

   if request.method == 'POST':
      if request.user.groups.filter(name='Managers').exists():
         serialized_item = CategorySerializer(data=request.data)
         serialized_item.is_valid(raise_exception=True)
         serialized_item.save()
         return Response(serialized_item.data, status.HTTP_201_CREATED)
      else:
         return Response({"message":"You are not authorized"}, 403)


#LIST ALL MENU ITEMS
@api_view(['GET', 'POST'])
@throttle_classes([AnonRateThrottle])
def menu_items(request):

   if request.method == 'GET':
      items = MenuItem.objects.all()

      to_price = request.query_params.get('to_price')
      ordering = request.query_params.get('ordering')
      perpage = request.query_params.get('perpage', default=2)
      page = request.query_params.get('page', default=1)

      if to_price:
         items = items.filter(price__lte=to_price)
      if ordering:
         ordering_fields = ordering.split(",")
         items = items.order_by(ordering)
      paginator = Paginator(items,per_page=perpage)
      try:
         items = paginator.page(number=page)
      except EmptyPage:
         items = []

      serialized_item = MenuItemSerializer(items, many=True)
      return Response(serialized_item.data, status.HTTP_200_OK)

   if request.method == 'POST':
      if request.user.groups.filter(name='Managers').exists():
         serialized_item = MenuItemSerializer(data=request.data)
         serialized_item.is_valid(raise_exception=True)
         serialized_item.save()
         return Response(serialized_item.data, status.HTTP_201_CREATED)
      else:
         return Response({"message":"You are not authorized"}, 403)

#SINGLE ITEM
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@throttle_classes([AnonRateThrottle])
def single_item(request, id):

   if request.method == 'GET':
      item = MenuItem.objects.get(pk=id)
      serialized_item = MenuItemSerializer(item)
      return Response(serialized_item.data, status.HTTP_200_OK)

   if request.method == 'PUT':
      if request.user.groups.filter(name='Manager').exists():
         item = MenuItem.objects.get(pk=id)
         serialized_item = MenuItemSerializer(item, data=request.data)
         serialized_item.is_valid(raise_exception=True)
         serialized_item.save()
         return Response(serialized_item.data, status.HTTP_200_OK)
      else:
         return Response({"message":"You are not authorized"}, 403)

   if request.method == 'PATCH':
      if request.user.groups.filter(name='Manager').exists():
         item = MenuItem.objects.get(pk=id)
         serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
         serialized_item.is_valid(raise_exception=True)
         serialized_item.save()
         return Response(serialized_item.data, status.HTTP_200_OK)
      else:
         return Response({"message":"You are not authorized"}, 403)

   if request.method == 'DELETE':
      if request.user.groups.filter(name='Manager').exists():
         item = MenuItem.objects.get(pk=id)
         item.delete()
         return Response(status.HTTP_204_NO_CONTENT)
      else:
         return Response({"message":"You are not authorized"}, 403)



#ADD TO CART FUNCTIONALITY
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
def cart(request):

   if request.method == "GET":
      cart = Cart.objects.all()
      serialized_item = CartSerializer(cart, many=True, context={'request': request})
      return Response(serialized_item.data, status.HTTP_200_OK)

   if request.method == "POST":
        serialized_item = CartSerializer(data=request.data, context={'request': request})
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(status=201, data={'message': 'Item added to cart!'})

   if request.method == "DELETE":
      Cart.objects.all().filter(user=request.user).delete()
      return Response(status.HTTP_204_NO_CONTENT)


#ALL ORDER ITEM FUNCTIONALITY
"""@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle])
def orders(request):

#GET ALL ORDER ITEM
   if request.method == "GET":
      if request.user.is_superuser:
         return Order.objects.all()
      elif request.user.groups.filter(name='Managers').exists():
         query = Order.objects.all()
         return query
      elif request.user.groups.filter(name='Delivery crew').exists():
         query = Order.objects.all().filter(delivery_crew=request.user)
         return query
      else:
         query = Order.objects.all(user=request.user)
      return query"""



# ORDER ITEMS
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.count()==0: #normal customer - no group
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Delivery Crew').exists(): #delivery crew
            return Order.objects.all().filter(delivery_crew=self.request.user)  #only show oreders assigned to him
        else: #delivery crew or manager
            return Order.objects.all()

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message:": "no item in cart"})

        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if (order_serializer.is_valid()):
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=self.request.user).all()

            for item in items.values():
                orderitem = OrderItem(
                    order=order,
                    menuitem_id=item['menuitem_id'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                orderitem.save()

            Cart.objects.all().filter(user=self.request.user).delete() #Delete cart items

            result = order_serializer.data.copy()
            result['total'] = total
            return Response(order_serializer.data)

    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total


class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
            return Response('Not Ok')
        else: #everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)
