import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from shop.recommender import Recommender


def order_create(request):
    """
    view for creating customer order
    :param request:
    :return:
    """
    cart = Cart(request)
    form = OrderCreateForm()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            r = Recommender()
            cart_products = [item['product'] for item in cart]
            r.products_bought(cart_products)
            # clear the cart
            cart.clear()
            order_created.delay(order.id)
            # set the order id in the session
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect(reverse('payment:process'))
    return render(request,
                  'order/create.html',
                  {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Custom view for admin site to show details
    of the provided order.
    :param request:
    :param order_id:
    :return:
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    """
    Custom view for admin site to print pdf
    invoice for the provided order.
    :param request:
    :param order_id:
    :return:
    """
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[weasyprint.CSS(
                                               settings.STATIC_ROOT + '/css/pdf.css'
                                           )])
    return response
