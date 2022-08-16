from shop.models import Cart, Artwork


class CartCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if uuid := request.COOKIES.get('cart_uuid'):
            try:
                cart = Cart.objects.get(uuid=uuid)
                not_on_sale = Artwork.objects.filter(
                    cart__uuid=uuid,
                    on_sale=False).values_list('id',
                                               flat=True)
                not_on_sale_ids = list(not_on_sale)
                if not_on_sale:
                    cart.items.remove(*not_on_sale_ids)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
        else:
            cart = Cart.objects.create()
        response = self.get_response(request)
        response.set_cookie('cart_uuid', cart.uuid)

        return response

