from django.contrib import admin
from .models import Artist, Artwork, Cart, Customer, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ('customer', 'items', 'order_date',
              'status', 'commentary')}),
         (None,
        {'fields': ('total_price',)})
    )

    readonly_fields = ('total_price',)

admin.site.register(Artist)
admin.site.register(Artwork)
admin.site.register(Cart)
admin.site.register(Customer)
# Register your models here.
