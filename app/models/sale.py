from random import choice, choices
from telnetlib import STATUS
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls.base import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from .order import Order
from .remittance import Remittance
from django.conf import settings
from model_utils.models import TimeStampedModel, StatusModel
from model_utils.managers import QueryManager

from model_utils.fields import StatusField

from app.constants import (
    SALE_STATUS_COMPLETE,
    SALE_STATUS_FOR_PICK_UP,
    SALE_STATUS_PENDING,
    SALE_STATUS_PROCESSING,
)


class Sale(TimeStampedModel):

    STATUS_CHOICES = Choices(
        (SALE_STATUS_PENDING, "Pending"),
        (SALE_STATUS_PROCESSING, "Processing"),
        (SALE_STATUS_FOR_PICK_UP, "For Pick Up"),
        (SALE_STATUS_COMPLETE, "Complete"),
    )

    remittance = models.ForeignKey(
        Remittance,
        on_delete=models.CASCADE,
        related_name="sales",
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales"
    )
    is_online = models.BooleanField(_("Online"), default=True)
    status = StatusField(choices_name="STATUS_CHOICES")
    notes = models.TextField(null=True, blank=True)
    is_ar = models.BooleanField(_("A/R"), default=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    or_number = models.CharField(
        _("OR Number"), max_length=50, help_text="", null=True, blank=True
    )

    objects = models.Manager()
    ar_closed = QueryManager(is_ar=True, remittance__is_active=False).order_by(
        "-remittance__date"
    )

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")

    def __str__(self):
        return f"{self.customer}"

    def get_absolute_url(self):
        return reverse("sale-detail", kwargs={"pk": self.pk})

    @property
    def debit_amount(self):
        return sum(debit.amount for debit in self.debits.all())

    @property
    def payment_amount(self):
        payment = 0
        if self.payment:
            payment = self.payment
        return payment

    @property
    def collected_amount(self):
        return self.debit_amount + self.payment_amount

    @property
    def balance(self):
        return self.total - self.collected_amount

    def set_ar(self):
        self.is_ar = self.balance > 0
        self.save()
        # if self.is_ar:
        self.remittance.check_ar()

    @property
    def sub_total(self):
        return round(sum(order.sub_total for order in self.orders.all()), 2)

    @property
    def discount_amount(self):
        return round(sum(order.discount_amount for order in self.orders.all()), 2)

    @property
    def type(self):
        return "Online" if self.is_online else "In-Store"

    @property
    def type_tag(self):
        return "primary" if self.is_online else "success"

    @property
    def status_tag(self):
        tags = {
            SALE_STATUS_PENDING: "warning",
            SALE_STATUS_COMPLETE: "success",
            SALE_STATUS_FOR_PICK_UP: "primary",
            SALE_STATUS_PROCESSING: "warning",
        }
        return tags[self.status]

    @property
    def total(self):
        return sum(order.total for order in self.orders.all())

    @property
    def display_notes(self):
        notes = list(order.note for order in self.orders.all())
        notes.append(self.notes)
        return " ".join(notes)

    @property
    def is_processing(self):
        return self.status == SALE_STATUS_PROCESSING

    @property
    def is_complete(self):
        return self.status == SALE_STATUS_COMPLETE

    def next(self, display=True):
        choices = list(self.STATUS_CHOICES)
        print(choices)
        print(self.status)
        current = [choice for choice in choices if self.status in choice][0]
        current_index = choices.index(current)
        current_index += 1
        # in-store transaction leads to complete
        if current_index == 2 and not self.is_online:
            current_index += 1
        if not display:
            return choices[current_index][0]
        return choices[current_index][1]

    def change_status(self):
        status = self.next(False)
        self.status = status
        if status == SALE_STATUS_PROCESSING:
            self.remittance = Remittance.objects.get(is_active=True)
        self.save()

    @property
    def ar_display(self):
        if self.is_ar:
            return "A/R"
        return "PAID"


def change_ar(sender, instance, **kwargs):
    instance.sale.set_ar()


post_save.connect(change_ar, sender=Order)
# post_save.connect(change_ar, sender=Debit)

post_delete.connect(change_ar, sender=Order)
# post_delete.connect(change_ar, sender=Debit)
