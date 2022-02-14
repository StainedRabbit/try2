from django_filters.widgets import RangeWidget
from dal import autocomplete
from dal.forward import Field
from app.models import Procurement
import csv

import django_filters
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Supplier
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic
import datetime
from django import forms
from django.http.response import Http404, HttpResponse

# filter
class ProcurementFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(
        field_name="date",
        label="Date",
        widget=RangeWidget(attrs={"type": "date", "class": "datepicker form-control"}),
    )

    supplier = django_filters.ModelChoiceFilter(
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(url="supplier-autocomplete"),
    )

    class Meta:
        model = Procurement
        fields = ["date", "supplier", "reference_number", "is_done"]


# form
class ProcurementForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(url="supplier-autocomplete"),
    )

    class Meta:
        model = Procurement
        exclude = ["is_done"]


@permission_required("products.can_manage_stock")
def procurement(request):
    filter = ProcurementFilter(request.GET, queryset=Procurement.objects.all())
    procurements = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))

    paginator = Paginator(procurements, 10)

    page = request.GET.get("page")
    try:
        procurements = paginator.page(page)
    except PageNotAnInteger:
        procurements = paginator.page(1)
    except EmptyPage:
        procurements = paginator.page(paginator.num_pages)

    context = {
        "procurements": procurements,
        "filter": filter,
        "has_filter": has_filter,
        "stock": "P",
    }
    return render(request, "app/procurement.html", context)


@permission_required("products.can_manage_stock")
def procurement_csv(request):
    # data = request.GET.copy()
    # if not data.get('start_date'):
    #     data['start_date'] = datetime.date.today()
    # if not data.get('end_date'):
    #     data['end_date'] = datetime.date.today()
    filter = ProcurementFilter(request.GET, queryset=Procurement.objects.all())
    procurements = filter.qs

    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)

    writer.writerow(
        [
            "SUPPLIER",
            "DATE",
            "REFERENCE #",
            "AMOUNT",
            "DONE",
        ]
    )

    for procurement in procurements:
        writer.writerow(
            [
                procurement.supplier,
                procurement.date,
                procurement.reference_number,
                procurement.amount,
                procurement.is_done,
            ]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Procurement Report - {datetime.date.today()}.csv"'
    return response


class ProcurementCreate(PermissionRequiredMixin, CreateView):
    permission_required = "products.can_manage_stock"
    model = Procurement
    form_class = ProcurementForm
    initial = {"date": datetime.date.today}

    def get_form(self):
        from django.forms.widgets import SelectDateWidget

        form = super(ProcurementCreate, self).get_form()
        form.fields["date"].widget = SelectDateWidget()
        return form

    def get_context_data(self, **kwargs):
        ctx = super(ProcurementCreate, self).get_context_data(**kwargs)
        ctx["stock"] = "P"
        return ctx


class ProcurementDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = "products.can_manage_stock"
    model = Procurement


class ProcurementUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "products.can_manage_stock"
    model = Procurement
    # Not recommended (potential security issue if more fields added)
    form_class = ProcurementForm

    def dispatch(self, request, *args, **kwargs):
        # self.procurement = get_object_or_404(Procurement, pk=kwargs['pk'])
        procurement = self.get_object()
        if procurement.is_done:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        from django.forms.widgets import SelectDateWidget

        form = super(ProcurementUpdate, self).get_form()
        form.fields["date"].widget = SelectDateWidget()
        return form


class ProcurementDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "products.can_manage_stock"
    model = Procurement
    success_url = reverse_lazy("procurement")

    def dispatch(self, request, *args, **kwargs):
        # self.procurement = get_object_or_404(Procurement, pk=kwargs['pk'])
        procurement = self.get_object()
        if procurement.is_done:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


@permission_required("users.can_administer")
def procurement_open(request, pk):
    procurement = get_object_or_404(Procurement, pk=pk)
    if request.method == "POST":
        procurement.is_done = False
        procurement.save()
        return redirect("procurement-detail", pk=procurement.pk)
    else:
        return render(
            request, "app/procurement_confirm_open.html", {"procurement": procurement}
        )


@permission_required("products.can_manage_stock")
def procurement_close(request, pk):
    procurement = get_object_or_404(Procurement, pk=pk)
    if request.method == "POST":
        procurement.is_done = True
        procurement.save()
        return redirect("procurement-detail", pk=procurement.pk)
    else:
        return render(
            request, "app/procurement_confirm_close.html", {"procurement": procurement}
        )
