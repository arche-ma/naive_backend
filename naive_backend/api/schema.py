
from graphql import GraphQLError
import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from shop.models import Artist, Artwork, Cart, Customer, Order
from graphene import Enum, Scalar

from .serializers import CustomerInputSerializer, OrderInputSerializer


class ObjectField(Scalar):
    @staticmethod
    def serialize(dt):
        return dt


class StatusChoices(Enum):
    NEW = 'NEW'
    ACCEPTED = 'ACCEPTED'
    PAID = 'PAID'
    CLOSED = 'CLOSED'
    CANCELLED = 'CANCELLED'


class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        fields = ('id', 'name', 'artworks', 'bio')
    
    image_url = graphene.String()
    
    def resolve_image_url(self, info):
        url = info.context.build_absolute_uri(self.image.url)
        return url

    def resolve_artworks(self, info):
        return self.artworks.filter(on_sale=True)


class ArtworkType(DjangoObjectType):
    class Meta:
        model = Artwork
        fields = ('id', 'title', 'description',
                  'author', 'price', 'year', 'size_width',
                  'size_height', 'on_sale')

    image_url = graphene.String()

    def resolve_image_url(self, info):
        url = info.context.build_absolute_uri(self.image.url)
        return url


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class CartType(DjangoObjectType):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


class CartMutation(graphene.Mutation):
    class Arguments:
        items = graphene.List(graphene.Int)
        uuid = graphene.String()

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(cls, root, info, uuid, items):
        cart = Cart.objects.get(pk=uuid)
        items = Artwork.objects.filter(pk__in=items, on_sale=True)
        cart.items.set(items)
        cart.save()
        return CartMutation(cart=cart)


class CustomerInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    surname = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)
    address = graphene.String()


class OrderInput(graphene.InputObjectType):
    commentary = graphene.String(required=False)
    items = graphene.List(graphene.Int)
    status = StatusChoices()


class CreateOrder(graphene.Mutation):
    class Arguments:
        cart = graphene.String(required=True)
        customer = CustomerInput(required=True)
        order = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = ObjectField()

    @classmethod
    def mutate(cls, root, info, customer, order, cart):
        customer_serializer = CustomerInputSerializer(data=customer)
        if customer_serializer.is_valid():
            customer = customer_serializer.save()
        else:
            msg = customer_serializer.errors
            return cls(message=msg, order=None)
        try:
            cart = Cart.objects.get(pk=cart)
        except Cart.DoesNotExist:
            msg = 'cart object does not exist'
            return cls(order=None, message=msg)

        items = cart.items.all()
        if items:
            order = Order(customer=customer,
                          commentary=order.commentary)
            order.save()
            order.items.set(cart.items.all())
            cart.items.update(on_sale=False)
            cart.items.clear()
            msg = 'success'
        else:
            msg = 'cart is empty'
            print(msg)
            return cls(order=None, message=msg)


        return CreateOrder(order=order, message=msg)


class UpdateOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        order = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = ObjectField()

    @classmethod
    def mutate(cls, root, info, id, order):
        requested_order = Order.objects.get(id=id)
        serializer = OrderInputSerializer(requested_order,
                                          data=order,
                                          partial=True)
        if serializer.is_valid():
            requested_order = serializer.save()
            msg = 'success'
        else:
            msg = serializer.errors
            requested_order = None
        return cls(order=requested_order, message=msg)
        


class UpdateCustomer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        customer = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)

    @classmethod
    def mutate(cls, root, info, id, customer):
        requested_customer = Customer(id=id)
        requested_customer.first_name = customer.first_name
        requested_customer.surname = customer.surname
        requested_customer.address = customer.address
        requested_customer.email = customer.email
        requested_customer.phone = customer.phone
        requested_customer.save()
        return UpdateCustomer(customer=requested_customer)


class Mutation(graphene.ObjectType):
    update_cart = CartMutation.Field()
    create_oder = CreateOrder.Field()
    update_order = UpdateOrder.Field()
    update_customer = UpdateCustomer.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(graphene.ObjectType):
    all_artworks = graphene.List(ArtworkType)
    all_artists = graphene.List(ArtistType)
    artist_by_id = graphene.Field(ArtistType,
                                  id=graphene.ID(required=True))

    artwork_by_id = graphene.Field(ArtworkType,
                                   id=graphene.ID(required=True))
    cart_by_id = graphene.Field(CartType, id=graphene.String(required=True))
    all_orders = graphene.List(OrderType)
    all_customers = graphene.List(CustomerType)

    def resolve_all_artworks(root, info):
        return Artwork.objects.select_related('author').filter(on_sale=True)
    
    def resolve_all_artists(root, info):
        return Artist.objects.prefetch_related('artworks').all()

    def resolve_all_orders(root, info):
        if info.context.user.is_superuser:
            return Order.objects.all()
        raise GraphQLError('permission denied')

    def resolve_artwork_by_id(root, info, id):
        try:
            return Artwork.objects.get(pk=id, artworks__on_sale=True)
        except Artwork.DoesNotExist:
            return None

    def resolve_artist_by_id(root, info, id):
        try:
            return Artist.objects.get(pk=id)
        except Artist.DoesNotExist:
            return None

    def resolve_cart_by_id(root, info, id):
        try:
            return Cart.objects.get(pk=id)
        except Cart.DoesNotExist:
            return None


schema = graphene.Schema(query=Query, mutation=Mutation)
