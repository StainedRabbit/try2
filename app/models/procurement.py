from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class Procurement(TimeStampedModel):
    supplier = models.ForeignKey(
        "app.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="procurements",
    )
    date = models.DateField()
    reference_number = models.CharField(max_length=50, help_text="")
    is_done = models.BooleanField(_("Done"), default=False)

    class Meta:
        verbose_name = _("Procurement")
        verbose_name_plural = _("Procurements")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.supplier} - {self.reference_number}"

    @property
    def amount(self):
        return sum(purchase.amount for purchase in self.purchases.all())

    def get_absolute_url(self):
        return reverse("procurement-detail", kwargs={"pk": self.pk})
