from django.db import models

from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid


User = get_user_model()


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.first_name + ' ' + self.surname


class Artist(models.Model):
    name = models.CharField(verbose_name='Имя',
                            max_length=250, null=False)
    bio = models.TextField(verbose_name='Биография')

    image = models.ImageField()

    def __str__(self) -> str:
        return self.name


class Artwork(models.Model):
    title = models.CharField(verbose_name='Название',
                             max_length=250)
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(Artist, related_name='artworks',
                               on_delete=models.CASCADE)
    technique = models.CharField(verbose_name='Техника',
                                 max_length=200)
    price = models.DecimalField(max_digits=9,
                                decimal_places=2)
    year = models.IntegerField()
    size_width = models.IntegerField(verbose_name='Высота')
    size_height = models.IntegerField(verbose_name='Ширина')
    image = models.ImageField()
    on_sale = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class Cart(models.Model):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    items = models.ManyToManyField(Artwork)

    def __str__(self) -> str:
        return f'{self.uuid}'


class Order(models.Model):
    NEW = 'NEW'
    ACCEPTED = 'ACCEPTED'
    PAID = 'PAID'
    CLOSED = 'CLOSED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [(NEW, 'NEW'), (ACCEPTED, 'ACCEPTED'), (PAID, 'PAID'),
                      (CLOSED, 'CLOSED'), (CANCELLED, 'CANCELLED')]

    customer = models.ForeignKey(Customer, related_name='orders',
                                 null=True,
                                 on_delete=models.SET_NULL)
    items = models.ManyToManyField(Artwork)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10,
                              default=NEW)
    commentary = models.TextField()

    @property
    def total_price(self):
        return sum(item.price for item in self.items.all())

    def __str__(self) -> str:
        return f'order N {self.id}'

