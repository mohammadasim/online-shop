from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon


class Cart(object):
    """
    Representing cart in the shop.
    A cart is a dictionary of dictionaries.
    The keys are the product ids and the values
    are dictionaries containing the corresponding
    product price and quantity.
    """

    def __init__(self, request):
        """
        initialise the cart
        """
        # store session to self.session to make it
        # available for other methods of the class
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity
        :param product:
        :param quantity:
        :param override_quantity:
        :return:
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as 'modified' to make sure
        # it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart
        :param product:
        :return:
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # We implement the iterator protocol by implementing
    # the __iter__ method in the class. This will allow
    # us to use for loop on an instance of our cart class

    def __iter__(self):
        """
        Iterate of the items in the cart and get the products
        from the database.
        :return:
        """
        product_ids = self.cart.keys()
        # get the product object and add them to the cart
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # returns a generator
            yield item

    def __len__(self):
        """
        count all items in the cart
        :return:
        """
        # the difference between iterator and generator is
        # that in generators we use () instead of []
        # In generators we can iterate over it only once.
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Returns the total price of the cart
        """
        return sum(item['price'] * item['quantity'] for item
                   in self.cart.values())

    def clear(self):
        """
        Remove cart from session
        :return:
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    @property
    def coupon(self):
        """
        Using @property so coupon is accessed
        via this method not directly. Hence acting
        as getter method.
        :return:
        """
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return self.coupon.discount / Decimal(100) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()