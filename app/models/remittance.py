from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class Remittance(TimeStampedModel):
    date = models.DateField(null=True)
    expenses = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, blank=True
    )
    cash = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    coins = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    is_locked = models.BooleanField(_("Locked"), default=False)
    notes = models.TextField(null=True, blank=True)
    with_ar = models.BooleanField(_("With A/R"), default=True)

    class Meta:
        verbose_name = _("Remittance")
        verbose_name_plural = _("Remittances")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date}"

    @property
    def latest_sales(self):
        return self.sales.all().order_by("-created")[:10]

    def get_absolute_url(self):
        return reverse("remittance-detail", kwargs={"pk": self.pk})

    def check_ar(self):
        ar = self.sales.filter(is_ar=True)
        if ar:
            self.with_ar = True
        else:
            self.with_ar = False
        self.save()

    @property
    def online_orders(self):
        return self.sales.filter(is_online=True)

    @property
    def in_store_orders(self):
        return self.sales.filter(is_online=False)

    @property
    def sub_total(self):
        return sum(sale.sub_total for sale in self.sales.all())

    @property
    def discount_amount(self):
        return sum(sale.discount_amount for sale in self.sales.all())

    @property
    def balance(self):
        return sum(sale.balance for sale in self.sales.all())

    @property
    def payment_amount(self):
        return sum(sale.payment_amount for sale in self.sales.all())

    @property
    def debit_amount(self):
        return sum(sale.debit_amount for sale in self.sales.all())

    @property
    def total(self):
        return sum(sale.total for sale in self.sales.all())

    @property
    def remitted_amount(self):
        return self.expenses + self.cash + self.coins

    @property
    def lack_over(self):
        return round(self.remitted_amount - self.payment_amount, 2)
