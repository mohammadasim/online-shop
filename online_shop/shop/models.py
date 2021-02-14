from django.db import models
from django.urls import reverse
from easy_thumbnails.fields import ThumbnailerImageField
from django_prometheus.models import ExportModelOperationsMixin
from parler.models import TranslatableModel, TranslatedFields


class Category(ExportModelOperationsMixin('category'), TranslatableModel):
    """
    Catalogue for the shop
    """
    translations = TranslatedFields(
        name=models.CharField(max_length=200,
                              db_index=True, ),
        slug=models.SlugField(max_length=200,
                              db_index=True,
                              unique=True)
    )

    class Meta:
        # Commented for model translations.
        # ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])


class Product(ExportModelOperationsMixin('product'), TranslatableModel):
    """
    Product in the shop
    """
    translations = TranslatedFields(
        name=models.CharField(max_length=200, db_index=True),
        slug=models.SlugField(max_length=200, db_index=True),
        description=models.TextField(blank=True)
    )
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='products')

    image = ThumbnailerImageField(upload_to='products/%Y/%m/%d',
                                  blank=True,
                                  resize_source=dict(size=(100, 100), sharpen=True))
    # Always use DecimalField to store monetary amounts
    # FloatField uses python's float type internally, whereas
    # DecimalField uses python's Decimal type. By using
    # the Decimal type, you will avoid float rounding issues.
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Commented for model translations.
    # class Meta:

    # ordering = ('name',)
    # we plan to query products by both id and slug
    # both fields are indexed together to improve
    # performance for queries that utilize the two fields.
    # index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])
