from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from app.models import remittance
from .user import User
from .sale import Sale


class CutOff(TimeStampedModel):
    date = models.DateField(_("Date"), auto_now=False, auto_now_add=False)
    is_done = models.BooleanField(_("Done"), default=False)

    class Meta:
        verbose_name = _("Cut Off")
        verbose_name_plural = _("Cut Offs")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date}"

    def get_absolute_url(self):
        return reverse("cut-off-detail", kwargs={"pk": self.pk})

    @property
    def amount(self):
        return sum(collection.amount for collection in self.collections.all())

    @property
    def transactions(self):
        # TODO: refactor this to eliminate the loop through all the records of the members. this will cause performance issue
        with_balances = []
        with_payments = []
        # TODO: filter only those in member group - add manager
        for customer in User.objects.all():
            collection = self.collections.filter(customer=customer).first()
            if collection:
                customer.payment = collection.amount
                balance = sum(debit.sale.balance for debit in collection.debits.all())
                customer.balance = balance
                customer.collection = collection
                with_payments.append(customer)
            else:
                ars = Sale.ar_closed.filter(
                    customer=customer, remittance__date__lte=self.date
                )
                balance = sum(ar.balance for ar in ars)
                customer.balance = balance
                if balance > 0:
                    with_balances.append(customer)

        return with_balances, with_payments
