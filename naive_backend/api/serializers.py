from rest_framework import serializers

from shop.models import Artwork, Customer, Order


class CustomerInputSerializer(serializers.ModelSerializer):
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Customer
        fields = ('first_name', 'surname', 'address',
                  'email', 'phone')


class OrderInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
