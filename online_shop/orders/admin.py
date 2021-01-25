from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    We use a ModelInline class for the orderItem
    model to include it as an inline in the
    OrderAdmin class. An inline allows you to include
    a model on the same edit page as its related model.
    """
    model = OrderItem
    """By default, Django’s admin uses a select-box interface (<select>) for fields that are ForeignKey. Sometimes 
    you don’t want to incur the overhead of having to select all the related instances to display in the drop-down. 
    raw_id_fields is a list of fields you would like to change into an Input widget for either a ForeignKey or 
    ManyToManyField: """
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
