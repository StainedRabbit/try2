from django.dispatch import receiver
from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager


class Product(TimeStampedModel):
    category = models.ForeignKey(
        "app.Category",
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=True)
    factor = models.DecimalField(
        _("Factor"), max_digits=5, decimal_places=2, null=True, blank=True
    )
    label = models.CharField(max_length=5)

    objects = models.Manager()
    active = QueryManager(is_active=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    @property
    def price(self):
        return self.prices.get(is_active=True)

    @property
    def inventory(self):
        return (
            float(self.get_purchase())
            + float(self.get_adjustment())
            - float(self.get_order())
        )

    @property
    def inventory_amount(self):
        return self.inventory * float(self.price.amount)

    def get_purchase(self, date=None):
        if date:
            return sum(
                purchase.quantity
                for purchase in self.purchases.filter(
                    procurement__date__lte=date, procurement__is_done=True
                )
            )
        return sum(
            purchase.quantity
            for purchase in self.purchases.filter(procurement__is_done=True)
        )

    def get_order(self, date=None):
        if date:
            return sum(
                order.quantity for order in self.orders.filter(sale__date__lte=date)
            )
        return sum(order.quantity for order in self.orders.all())

    def get_adjustment(self, date=None):
        if date:
            return sum(
                adjustment.quantity
                for adjustment in self.adjustments.filter(date__lte=date)
            )
        return sum(adjustment.quantity for adjustment in self.adjustments.all())


@receiver(post_save, sender=Product)
def create_price(sender, instance, created, **kwargs):
    if created:
        instance.prices.create(amount=0)
