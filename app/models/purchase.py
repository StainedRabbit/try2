from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Purchase(models.Model):
    procurement = models.ForeignKey(
        "app.Procurement", on_delete=models.CASCADE, related_name="purchases"
    )
    product = models.ForeignKey(
        "app.Product", on_delete=models.CASCADE, related_name="purchases"
    )
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")

    def __str__(self):
        return f"{self.product}"

    def get_absolute_url(self):
        return reverse("purchase-detail", kwargs={"pk": self.pk})
