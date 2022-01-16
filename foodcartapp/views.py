import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    response = request.data
    if (not (address := response.get('address')) or
            not isinstance(address, str)):
        return Response(
            {"error": "address key not presented or not str"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif (not (firstname := response.get('firstname')) or
          not isinstance(firstname, str)):
        return Response(
            {"error": "firstname key not presented or not str"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif (not (lastname := response.get('lastname')) or
          not isinstance(lastname, str)):
        return Response(
            {"error": "lastname key not presented or not str"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif (not (phonenumber := response.get('phonenumber')) or
          not isinstance(phonenumber, str)):
        return Response(
            {"error": "phonenumber key not presented or not str"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif (not (products := response.get('products')) or
          not isinstance(products, list)):
        return Response(
            {"error": "products key not presented or not list"},
            status=status.HTTP_400_BAD_REQUEST
        )

    pure_phonenumber = phonenumbers.parse(phonenumber, 'RU')
    if not phonenumbers.is_valid_number(pure_phonenumber):
        return Response(
            {"error": "non-existent phone number"},
            status=status.HTTP_400_BAD_REQUEST
        )
    phonenumber = phonenumbers.format_number(
        pure_phonenumber,
        phonenumbers.PhoneNumberFormat.E164
    )

    product_quantities = [product.get('quantity') for product in products]
    if (not all(product_quantities) or
        not all(isinstance(quantity, int) for quantity in product_quantities) or
            any(quantity < 1 for quantity in product_quantities)):
        return Response(
            {"error": "quantity key not presented or incorrect"},
            status=status.HTTP_400_BAD_REQUEST
        )

    product_ids = [product.get('product') for product in products]
    products = Product.objects.all()
    possible_product_ids = [product.id for product in products]
    if (not all(product_ids) or
            any(product_id not in possible_product_ids
                for product_id in product_ids)):
        return Response(
            {"error": "product key not presented or incorrect"},
            status=status.HTTP_400_BAD_REQUEST
        )
    order = Order.objects.create(
        address=address,
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber
    )
    for position in response['products']:
        product = Product.objects.get(pk=position['product'])
        order_item = OrderItem(
            order=order,
            product=product,
            count=position['quantity']
        )
        order_item.save()
    return Response(
        {"success": "order added"}
    )
