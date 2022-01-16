import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField, RelatedField
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer

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


class OrderItemSerializer(ModelSerializer):
    product = PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def validate(self, data):
        if data['quantity'] < 1:
            raise ValidationError(
                {"quantity": "Недопустимое количество товара"}
            )
        return data


class OrderSerializer(ModelSerializer):
    phonenumber = PhoneNumberField()
    products = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['address', 'firstname', 'lastname',
                  'phonenumber', 'products']
        extra_kwargs = {
            "phonenumber": {
                "validators": [],
            },
        }

    def validate(self, data):
        try:
            pure_phonenumber = phonenumbers.parse(data['phonenumber'], 'RU')
        except NumberParseException:
            raise ValidationError(
                {"phonenumber": "Некорректный номер телефона"}
            )
        if not phonenumbers.is_valid_number(pure_phonenumber):
            raise ValidationError(
                {"phonenumber": "Некорректный номер телефона"}
            )
        data['phonenumber'] = phonenumbers.format_number(
            pure_phonenumber,
            phonenumbers.PhoneNumberFormat.E164
        )
        return data

    def create(self, validated_data):
        order = Order.objects.create(
            address=validated_data['address'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber']
        )
        order_items = [OrderItem(order=order, **product) for product in
                       validated_data['products']]
        OrderItem.objects.bulk_create(order_items)
        return order


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {"success": "Заказ добавлен"}
    )
