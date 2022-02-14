from venv import create
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls.base import reverse
from model_utils.models import TimeStampedModel


class Adjustment(TimeStampedModel):
    product = models.ForeignKey(
        "app.Product", on_delete=models.CASCADE, related_name="adjustments"
    )
    quantity = models.FloatField(default=0)
    notes = models.TextField()

    class Meta:
        verbose_name = _("Adjustment")
        verbose_name_plural = _("Adjustments")

    def __str__(self):
        return f"{self.product} {self.quantity}"

    # def get_absolute_url(self):
    #     return reverse("Adjustment_detail", kwargs={"pk": self.pk})
