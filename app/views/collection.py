from django_filters.widgets import RangeWidget
from dal import autocomplete
from dal.forward import Field
from app.models import Procurement
import csv
from django.core.exceptions import ValidationError

import django_filters
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic
import datetime
from django import forms
from django.http.response import Http404, HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from app.models import Collection, User, CutOff, Sale


class CollectionCreate(PermissionRequiredMixin, CreateView):
    permission_required = "products.can_manage_stock"
    model = Collection
    fields = [
        "amount",
    ]

    def get_initial(self):
        return {
            "amount": self.balance,
        }

    def form_valid(self, form):
        # TODO: make sure na mavalidate na di na malapas yung bayad
        form.instance.cut_off = self.cut_off
        form.instance.customer = self.customer
        return super(CollectionCreate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(User, pk=kwargs["customer_id"])
        self.cut_off = get_object_or_404(CutOff, pk=kwargs["cut_off_id"])

        ars = Sale.ar_closed.filter(
            customer=self.customer, created__lte=self.cut_off.date
        ).order_by("created")
        self.balance = sum(ar.balance for ar in ars)
        self.ars = ars
        # if self.procurement.is_done:
        #     raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # id = self.kwargs.get('pk')
        # procurement = Procurement.objects.get(id=id)
        ctx = super(CollectionCreate, self).get_context_data(**kwargs)
        ctx["customer"] = self.customer
        ctx["cut_off"] = self.cut_off
        ctx["ars"] = self.ars
        return ctx

    def get_success_url(self):
        # self.collection.check_detail.add(self.object)
        collection = self.object
        amount = collection.amount
        # create debit
        for ar in self.ars:
            if amount > 0:
                is_paid = False
                if amount >= ar.balance:
                    is_paid = True
                    debit_amount = ar.balance
                else:
                    debit_amount = amount
                debit = collection.debits.create(
                    sale=ar, amount=debit_amount, is_paid=is_paid
                )
                amount -= ar.balance
            else:
                break
        return reverse("cut-off-detail", args=(self.cut_off.id,))


class CollectionDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "products.can_manage_stock"
    model = Collection
    # success_url = reverse_lazy('collection')

    # def dispatch(self, request, *args, **kwargs):
    #     # self.procurement = get_object_or_404(Procurement, pk=kwargs['pk'])
    #     collection = self.get_object()
    #     if collection.is_done:
    #         raise Http404
    #     return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("cut-off-detail", args=(self.object.cut_off.id,))
