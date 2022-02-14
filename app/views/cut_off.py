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

from app.models import CutOff, User, Sale


class CutOffFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(
        field_name="date",
        label="Date",
        widget=RangeWidget(attrs={"type": "date", "class": "datepicker form-control"}),
    )

    class Meta:
        model = CutOff
        fields = ["date", "is_done"]


@permission_required("products.can_manage_stock")
def cut_off(request):
    filter = CutOffFilter(request.GET, queryset=CutOff.objects.all())
    cut_offs = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))

    paginator = Paginator(cut_offs, 10)

    page = request.GET.get("page")
    try:
        cut_offs = paginator.page(page)
    except PageNotAnInteger:
        cut_offs = paginator.page(1)
    except EmptyPage:
        cut_offs = paginator.page(paginator.num_pages)

    context = {
        "cut_offs": cut_offs,
        "filter": filter,
        "has_filter": has_filter,
    }
    return render(request, "app/cut_off.html", context)


class CutOffCreate(PermissionRequiredMixin, CreateView):
    permission_required = "products.can_manage_stock"
    model = CutOff
    fields = ["date"]
    initial = {"date": datetime.date.today}

    def get_form(self):
        from django.forms.widgets import SelectDateWidget

        form = super(CutOffCreate, self).get_form()
        form.fields["date"].widget = SelectDateWidget()
        return form

    def get_context_data(self, **kwargs):
        ctx = super(CutOffCreate, self).get_context_data(**kwargs)
        ctx["stock"] = "P"
        return ctx


class CutOffDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = "products.can_manage_stock"
    model = CutOff

    def get_context_data(self, **kwargs):
        ctx = super(CutOffDetail, self).get_context_data(**kwargs)
        ctx["with_balances"], ctx["with_payments"] = self.object.transactions
        return ctx


class CutOffDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "products.can_manage_stock"
    model = CutOff
    success_url = reverse_lazy("cut-off")


@permission_required("products.can_manage_stock")
def cut_off_close(request, pk):
    cut_off = get_object_or_404(CutOff, pk=pk)
    if request.method == "POST":
        cut_off.is_done = True
        cut_off.save()
        return redirect("cut-off-detail", pk=cut_off.pk)
    else:
        return render(request, "app/cut_off_confirm_close.html", {"cut_off": cut_off})


@permission_required("users.can_administer")
def cut_off_open(request, pk):
    cut_off = get_object_or_404(CutOff, pk=pk)
    if request.method == "POST":
        cut_off.is_done = False
        cut_off.save()
        return redirect("cut-off-detail", pk=cut_off.pk)
    else:
        return render(request, "app/cut_off_confirm_open.html", {"cut_off": cut_off})
