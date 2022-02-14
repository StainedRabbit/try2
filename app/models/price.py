from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls.base import reverse
from model_utils.models import TimeStampedModel


class Price(TimeStampedModel):
    product = models.ForeignKey(
        "app.Product", on_delete=models.CASCADE, related_name="prices"
    )
    is_active = models.BooleanField(_("Active"), default=True)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self):
        # return f'{self.product} - {self.amount}'
        return f"{self.amount}"

    def get_absolute_url(self):
        return reverse("price_detail", kwargs={"pk": self.pk})
