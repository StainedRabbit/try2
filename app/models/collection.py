from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Collection(models.Model):
    cut_off = models.ForeignKey(
        "app.CutOff",
        verbose_name=_("Cut Off"),
        on_delete=models.CASCADE,
        related_name="collections",
        null=True,
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Customer"),
        on_delete=models.CASCADE,
        related_name="collections",
        null=True,
    )
    amount = models.DecimalField(
        _("Amount"), max_digits=10, decimal_places=2, null=True
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __str__(self):
        return f"{self.customer} - {self.amount}"

    def get_absolute_url(self):
        return reverse("collection-detail", kwargs={"pk": self.pk})

    # @property
    # def amount(self):
    #     return sum(debit.amount for debit in self.debits.all())
