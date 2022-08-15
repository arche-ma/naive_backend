import graphene
from graphene_django import DjangoObjectType
from shop.models import Artist, Artwork, Cart, Customer, Order
from graphene import Enum


class StatusChoices(Enum):
    NEW = 'New'
    ACCEPTED = 'ACCEPTED'
    PAID = 'Paid'
    CLOSED = 'CLOSED'
    CANCELLED = 'CANCELLED'


class ArtistType(DjangoObjectType):
    class Meta:
        model = Artist
        fields = ('id', 'name', 'artworks')


class ArtworkType(DjangoObjectType):
    class Meta:
        model = Artwork
        fields = ('id', 'title', 'description',
                  'author')


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

    @classmethod
    def mutate(cls, root, info, customer, order, cart):
        customer = Customer(
            first_name=customer.first_name,
            surname=customer.surname,
            email=customer.email,
            phone=customer.phone
        )
        customer.save()
        cart_uuid = cart
        cart = Cart.objects.get(pk=cart_uuid)
        commentary = order.commentary
        for item in cart.items.all():
            item.on_sale = False
        order = Order(customer=customer,
                      commentary=commentary)
        order.save()
        order.items.set(cart.items.all())
        order.save()

        cart.items.clear()
        return CreateOrder(order=order)


class ChangeOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        order = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, id, order):
        try:
            requested_order = Order.objects.get(pk=id)
            requested_order.items.set(order.items)
            requested_order.status = order.status
            requested_order.commentary = order.commentary
            requested_order.save()
            return ChangeOrder(order=requested_order)
        except Order.DoesNotExist as e:
            return e


class ChangeCustomer(graphene.Mutation):
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
        return ChangeCustomer(customer=requested_customer)


class Mutation(graphene.ObjectType):
    update_cart = CartMutation.Field()
    create_oder = CreateOrder.Field()
    update_order = ChangeOrder.Field()
    update_customer = ChangeCustomer.Field()


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
    
    def resolve_all_orders(root, info):
        if info.context.user.is_superuser:
            return Order.objects.all()
        return {'error':'Not an admin'}
    
    def resolve_artwork_by_id(root, info, id):
        try:
            return Artwork.objects.get(pk=id)
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

