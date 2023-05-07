# LITTLE LEMON API APP.

Source code url:
   https://github.com/MegaNAD60/little-lemon-API

This is a fully CRUD functional app built which allows users to register, browse through all menu items
and provide the functionality to add to cart and make orders. It also allows the Admin to create groups
and assign these groups to staffs.

Building this app included lots of dependencies which were installed using pipenv, a tool that provides
all necessary means to create a virtual environment for python projects.

## DEPENDENCIES
Django
Django rest_framework,
Djoser.

## USERS, GROUPS AND THEIR PASSWORD
### Admin:
    username: Nehemiah
    password: nehe0000

### Managers:
    username: Nehemiah
    password: nehe0000

    username: Alex
    password: alex0000

### Delivery Crew:
    username: John
    password: John0000

    username: Peace
    password: peace0000

### Customers:
    username: Peter
    password: peter0000

    username: Paul
    password: paul0000


## URL PATH TO GO
To create a new users, with a POST request, visit:
    http://127.0.0.1:8000/api/users/

To generate token for users, with a POST request, visit:
   http://127.0.0.1:8000/api/token/login/

To access current user, with a GET request and accurate token, visit:
   http://127.0.0.1:8000/api/users/users/me/

To access all users as a manager only, with a GET request, visit:
   http://127.0.0.1:8000/api/users/

To add users into manager group as a manager, with a POST request, visit:
   http://127.0.0.1:8000/api/groups/manager/users/

To access all users with manager status done by a manager only, with  a GET request, visit:
   http://127.0.0.1:8000/api/groups/manager/users/

To add users into delivery-crew group as a manager, with a POST request, visit:
   http://127.0.0.1:8000/api/groups/manager/users/

To access all users with delivery-crew status done by a manager only, with  a GET request, visit:
   http://127.0.0.1:8000/api/groups/manager/users/


## Also Do Note that:
Only managers can add menu items by using the GET request. For other users, you can only view menu-items
as well as access details of each menu items.
Also, note that categories field must first of all be created and then assign to each menu-items to be
created. Using GET to access categories and POST to create a new category, visit:
   http://127.0.0.1:8000/api/cateories/

To add menu-items as a manager, with a POST request, visit:
   http://127.0.0.1:8000/api/menu-items/

To access all menu-items, with a GET request, visit:
   http://127.0.0.1:8000/api/menu-items/

Each menu-items can be access using their various id. For example, to access a menu-item
with an id=1, visit
   http://127.0.0.1:8000/api/menu-items/1/

For managers, they can ADD, CHANGE, UPDATE, and DELETE any menu-items using POST, PUT,
PATCH and DELETE request respectively.


Users can add items to cart using the POST request. With a GET request, you access every items in your cart,
and with a DELETE request, you can delete items in your cart, using the link below.
   http://127.0.0.1:8000/api/cart/menu-items/


