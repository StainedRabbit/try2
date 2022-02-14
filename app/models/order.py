from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


import decimal


class Order(models.Model):
    DISCOUNT_TYPE_CHOICE = (
        ("P", "Percent"),
        ("C", "Count"),
        # ('M', 'Manual'),
    )

    sale = models.ForeignKey(
        "app.Sale", on_delete=models.CASCADE, related_name="orders"
    )
    product = models.ForeignKey(
        "app.Product", on_delete=models.CASCADE, related_name="orders"
    )
    discount_type = models.CharField(
        max_length=1, choices=DISCOUNT_TYPE_CHOICE, null=True, blank=True
    )
    discount_quantity = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    # order_type = models.CharField(
    #     max_length=1, choices=ORDER_TYPE_CHOICE, default='G')
    # quantity = models.PositiveIntegerField(
    #     null=True, blank=True)
    # prev_quantity = models.PositiveIntegerField(
    #     default=0)
    quantity = models.DecimalField(
        _("Quantity"), max_digits=5, decimal_places=2, null=True, blank=True
    )
    prev_quantity = models.DecimalField(
        _("Prev Quantity"), max_digits=5, decimal_places=2, null=True, blank=True
    )

    price = models.ForeignKey(
        "app.Price", on_delete=models.CASCADE, related_name="orders"
    )
    # flag to determine if the order is modified by admin
    is_modified = models.BooleanField(_("Modified"), default=False)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"{self.product}"

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"pk": self.pk})

    @property
    def sub_total(self):
        return self.quantity * self.price.amount

    @property
    def discount_amount(self):
        if not self.discount_type:
            return 0
        elif self.discount_type == "P":
            return round(self.quantity * (self.discount_quantity / 100), 2)
        else:
            return round(self.quantity * self.discount_quantity, 2)

    @property
    def total(self):
        return round(self.sub_total - decimal.Decimal(self.discount_amount), 2)

    @property
    def note(self):
        note = ""
        if self.sale.is_online and self.prev_quantity != self.quantity:
            note = f"{self} was changed from {self.prev_quantity} to {self.quantity}."
        return note
