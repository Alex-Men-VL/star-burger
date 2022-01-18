from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, OuterRef, Subquery, Sum
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def price(self):
        orders = self
        items = OrderItem.objects.filter(
            order=OuterRef('pk')
        ).values('order').annotate(
            total_price=Sum('price')).values('total_price')
        orders = orders.annotate(total_price=Subquery(items))
        return orders


class Order(models.Model):
    UNPROCESSED = 'NP'
    PROCESSED = 'P'
    DELIVERED = 'D'
    ORDER_STATUS_CHOICE = [
        (UNPROCESSED, 'не обработан'),
        (PROCESSED, 'обработан'),
        (DELIVERED, 'доставлен'),
    ]

    address = models.CharField(
        'адрес',
        max_length=100
    )
    firstname = models.CharField(
        'имя заказчика',
        max_length=20
    )
    lastname = models.CharField(
        'фамилия заказчика',
        max_length=20
    )
    phonenumber = PhoneNumberField(
        'контактный телефон'
    )
    products = models.ManyToManyField(
        Product,
        related_name='orders',
        verbose_name='товары',
        through='OrderItem',
    )
    status = models.CharField(
        'статус заказа',
        max_length=12,
        choices=ORDER_STATUS_CHOICE,
        default=UNPROCESSED,
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар'
    )
    quantity = models.IntegerField(
        'количество'
    )
    price = models.DecimalField(
        'стоимость позиции',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f'{self.product.name} {self.order.firstname} ' \
               f'{self.order.lastname} {self.order.address}'
