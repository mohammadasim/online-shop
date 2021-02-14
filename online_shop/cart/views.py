from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product

from coupons.forms import CouponApplyForm
from shop.recommender import Recommender

from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """
    view function for adding item to the cart
    :param request:
    :param product_id:
    :return:
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    View to remove product from cart
    :param request:
    :param product_id:
    :return:
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    view for cart details
    :param request:
    :return:
    """
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                'quantity': item['quantity'],
                'override': True
            }
        )
    coupon_apply_form = CouponApplyForm()
    r = Recommender()
    # Getting the product from cart items in the cart.
    # Each item in the cart has a product
    cart_products = [item['product'] for item in cart]
    # Passing the products to the recommendation engine
    recommended_products = r.suggest_products_for(cart_products, max_results=4)

    return render(request,
                  'cart/detail.html',
                  {
                      'cart': cart,
                      'coupon_apply_form': coupon_apply_form,
                      'recommended_products': recommended_products
                  })
