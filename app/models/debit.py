from django.db.models.fields import DateField
from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import QueryManager


class Debit(models.Model):
    collection = models.ForeignKey(
        "app.Collection",
        verbose_name=_("Collection"),
        related_name="debits",
        on_delete=models.CASCADE,
    )
    sale = models.ForeignKey(
        "app.Sale",
        verbose_name=_("Sale"),
        related_name="debits",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    objects = models.Manager()
    closed = QueryManager(collection__cut_off__is_done=True)
    paid_closed = QueryManager(is_paid=True, collection__cut_off__is_done=True)

    class Meta:
        verbose_name = _("Debit")
        verbose_name_plural = _("Debits")
        ordering = ["-sale"]

    def __str__(self):
        return f"{self.sale} - {self.amount}"

    def get_absolute_url(self):
        return reverse("debit-detail", kwargs={"pk": self.pk})

    def change_ar_debit(self):
        # check payment + collention
        self.sale.is_ar = self.sale.total > self.sale.collected_amount
        self.sale.save()

    def set_paid(self):
        self.is_paid = not self.sale.is_ar
        self.save()


from django.db.models.signals import post_save, post_delete


def change_ar_debit(sender, instance, **kwargs):
    instance.change_ar_debit()


post_save.connect(change_ar_debit, sender=Debit)
post_delete.connect(change_ar_debit, sender=Debit)
