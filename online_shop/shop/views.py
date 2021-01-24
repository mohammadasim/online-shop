from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Category, Product


def product_list(request, category_slug=None):
    """
     List products in provided category.
     :param request:
     :param category_slug:
     :return:
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


def product_detail(request, id, slug):
    """
    Details of a single product
    :param request:
    :param id:
    :param slug:
    :return:
    """
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    return render(request,
                  'product/detail.html',
                  {'product': product})
