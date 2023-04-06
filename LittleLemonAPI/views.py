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
      if request.user.groups.filter(name='Managers').exists():
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
@throttle_classes([AnonRateThrottle])
def cart(request):

   if request.method == "GET":
      cart = Cart.objects.filter(user=request.user)
      serialized_item = CartItemSerializer(cart)
      return (serialized_item.data, status.HTTP_200_OK)

   if request.method == "POST":
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price,
                                menuitem_id=id)
        except:
            return Response(status=409, data={'message': 'Item already in cart'})
        return Response(status=201, data={'message': 'Item added to cart!'})


#ALL ORDER ITEM FUNCTIONALITY
@api_view(['GET', 'POST', 'DELETE'])
@throttle_classes([AnonRateThrottle])
def orders(request):

   if request.method == "GET":
      if request.user.groups.filter(name='Managers').exists() or request.user.is_superuser == True:
         query = Order.objects.all()
      elif request.user.groups.filter(name='Delivery crew').exists():
         query = Order.objects.filter(delivery_crew=request.user)
      else:
         query = Order.objects.filter(user=request.user)
      return query

   if request.method == "POST":
        cart = Cart.objects.filter(user=request.user)
        x = cart.values_list()
        if len(x) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(x[-1]) for x in x])
        order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return Response(status=201, data={
            'message': 'Your order has been placed! Your order number is {}'.format(str(order.id))})


#SINGLE ORDERED ITEM FUNCTIONALITY
@api_view(['GET', 'POST', 'DELETE'])
@throttle_classes([AnonRateThrottle])
def single_orders(request, self):

   if request.method == "GET":
      query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
      return (query.data, status.HTTP_200_OK)

   if request.method == "PATCH":
      order = Order.objects.get(pk=self.kwargs['pk'])
      order.status = not order.status
      order.save()
      return Response(status=200,
                           data={'message': 'Status of order #' + str(order.id) + ' changed to ' + str(order.status)})
   if request.method == "PUT":
      serialized_item = OrderPutSerializer(data=request.data)
      serialized_item.is_valid(raise_exception=True)
      order_pk = self.kwargs['pk']
      crew_pk = request.data['delivery_crew']
      order = get_object_or_404(Order, pk=order_pk)
      crew = get_object_or_404(User, pk=crew_pk)
      order.delivery_crew = crew
      order.save()
      return Response(status=201,
                           data={'message': str(crew.username) + ' was assigned to order #' + str(order.id)})

   if request.method == "DELETE":
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return Response(status=200, data={'message': 'Order #{} was deleted'.format(order_number)})