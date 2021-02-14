import redis
from django.conf import settings
from .models import Product

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender(object):

    def get_product_key(self, id):
        """
        In this function we generate a key
        that is to be stored in redis for a
        proudct.
        :param id:
        :return:
        """
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        """
        The function receives a list of products.
        We loop throw the products using two loops,
        such that each the key product a is bought with product b
        and c and d etc by 1.
        The relationship where by product a is bought with proudct X
        that gets the highest number will be the product bouth together
        most of the time.
        :param products:
        :return:
        """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each other
                if product_id != with_id:
                    # increment score for product purchased together
                    r.zincrby(self.get_product_key(product_id),
                              1,
                              with_id)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # only 1 product
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True
            )[:max_results]
        else:
            # generate a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            # We create a temporary file with convention temp_<product_ids>
            # This is to ensure there never is a clash between to tmp_key in redis.
            tmp_key = f'tmp_{flat_ids}'
            # We then generate a list of all the redis keys for the products.
            # These redis keys are sets in redis
            keys = [self.get_product_key(id) for id in product_ids]
            # We then create a union of all the sets and save the results in temp_key.
            # The content of tmp_key will be <product_id>:<score>, the score represents
            # how many times the item with id in set name was bought with the item with
            # id in tmp_key.
            r.zunionstore(tmp_key, keys)
            # remove ids for the products the recommendation is for
            r.zrem(tmp_key, *product_ids)
            # get the product ids by their score, descendant sort
            suggestions = r.zrange(tmp_key, 0, -1,
                                   desc=True)[:max_results]
            # remove te temporary key
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        # get suggested products and sort by order of appearance
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        # get all the products in the shop as a list
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
