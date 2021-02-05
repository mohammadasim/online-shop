import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

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


def order_detail(obj):
    """
    Function that shows custom view for order detail.
    :param obj:
    :return:
    """
    url = reverse('orders:admin_order_detail', args=[obj.id])
    # Notice we using only single {} in url
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    """
    function that links the view admin_order_pdf
    to the admin site for order. The function returns
    a url to the view. This function is added to the
    list_display of the orderAdmin
    :param obj:
    :return:
    """
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = 'Invoice'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    # we add the custom action defined about to model admin class
    actions = ['export_to_csv']

    def export_to_csv(self, request, queryset):
        """
        Exports the orders provided in queryset to a
        csv file.
        :param request:
        :param queryset:
        :return:
        """
        # Get access to the model meta class.
        # This usually defined at the end of the model class
        opt = self.model._meta
        # create content_disposition, that is to be passed to the response.
        # here we tell that the response contains a file attachment and the
        # name of the file.
        content_disposition = f'attachment; filename={opt.verbose_name}.csv'
        # create an instance of HttpResponse, specifying the text/csv content
        # to tell the browser that the response has to be treated as a CSV file.
        # We also add Content-Disposition header to indicated that the http response
        # contains an attached file.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = content_disposition

        # We create a csv writer object that will write to the
        # response object.
        writer = csv.writer(response)
        # We get models fields dynamically, using the get_options method
        # of the model _meta options. We exclude m2m and m21 relationships.
        fields = [field for field in opt.get_fields()
                  if not field.many_to_many and not field.one_to_many]
        # write a first row with header information
        writer.writerow([field.verbose_name for field in fields])
        # write data rows
        # The queryset contains the list of instances, whose fields info we have
        # to export to csv file. so we iterate over each object in the queryset
        # we then change datetime fields of the object into strings
        # we then write the data to the writer.
        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field.name)
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y')
                data_row.append(value)
            writer.writerow(data_row)
        return response

    # We customise the display name of the action in the actions dropbox
    # element of the admin site by setting a short_description attribute of
    # the function.
    export_to_csv.short_description = 'Export to CSV'
