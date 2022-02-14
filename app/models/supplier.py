from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Supplier(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("supplier-detail", kwargs={"pk": self.pk})
