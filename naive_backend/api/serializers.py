from rest_framework import serializers

from shop.models import Artwork, Customer


class CustomerInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name', 'surname', 'address',
                  'email', 'phone')

class OrderInputSerializer(serializers.Serializer):
    items = serializers.IntegerField(many=True)
    commentary = serializers.CharField(blank=True)
    status = serializers.CharField(blank=False)

    def validate_items(self, items):
        for item in items:
            if not Artwork.objects.get(pk=item).exists():
                raise serializers.ValidationError(
                    'art object doesn\'t exist')
        return items
