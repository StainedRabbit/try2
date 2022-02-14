from django_filters.widgets import RangeWidget
from dal import autocomplete
from dal.forward import Field
from app.constants import SALE_STATUS_PROCESSING
from app.models import Procurement
import csv

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


from app.models import Sale, Remittance, User


class SaleForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     seller = kwargs.pop('seller', None)
    #     super(SaleForm, self).__init__(*args, **kwargs)
    #     # self.fields['date_sold'].initial = datetime.date.today
    #     self.fields['seller'].initial = seller

    # def clean(self):
    #     cleaned_data = super(SaleForm, self).clean()
    #     if cleaned_data['or_number']:
    #         # check or number exist if not blank
    #         exist = Sale.objects.filter(or_number=cleaned_data['or_number'])
    #         if self.instance:
    #             exist = exist.exclude(or_number=self.instance.or_number)
    #         if exist:
    #             raise ValidationError(
    #                 {'or_number': ValidationError(
    #                     _('OR Number already exist.'))}
    #             )

    #     return cleaned_data

    customer = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="customer-autocomplete", forward=["seller"]
        ),
    )

    # seller = forms.ModelChoiceField(
    #     widget=forms.HiddenInput(), queryset=Seller.objects.all())

    class Meta:
        model = Sale
        fields = ["customer", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class SaleFilter(django_filters.FilterSet):
    remittance__date = django_filters.DateFromToRangeFilter(
        label="Remittance Date",
        widget=RangeWidget(attrs={"type": "date", "class": "datepicker form-control"}),
    )

    customer = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="customer-autocomplete",
            forward=(Field("Remittance__seller", "seller"),),
        ),
    )

    class Meta:
        model = Sale
        fields = [
            "remittance__date",
            "customer",
            "or_number",
            "is_online",
            "status",
            "is_ar",
        ]


class SalePaymentForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            "payment",
        ]


def sale_csv(request):
    sales = Sale.objects.filter(remittance__is_active=False)
    filter = SaleFilter(request.GET, queryset=sales)
    sales = filter.qs
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)

    writer.writerow(
        [
            "REMITTANCE ID",
            "ID",
            "TYPE",
            "STATUS",
            "OR NUMBER",
            "CUSTOMER",
            "DATE",
            "SUBTOTAL",
            "DISCOUNT",
            "TOTAL",
            "PAYMENT",
            "DEBITTED",
            "BALANCE",
            "NOTES",
        ]
    )

    for sale in sales:
        writer.writerow(
            [
                sale.remittance.id,
                sale.id,
                sale.type,
                sale.get_status_display(),
                sale.or_number,
                sale.customer,
                sale.created.strftime("%Y-%m-%d %H:%M:%S"),
                sale.sub_total,
                sale.discount_amount,
                sale.total,
                sale.payment_amount,
                sale.debit_amount,
                sale.balance,
                "",
            ]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Sale Report - {datetime.date.today()}.csv"'
    return response


def sale(request):
    sales = Sale.objects.filter(remittance__is_active=False)
    filter = SaleFilter(request.GET, queryset=sales)
    sales = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))
    paginator = Paginator(sales, 10)

    page = request.GET.get("page")
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)

    context = {
        "sales": sales,
        "filter": filter,
        "has_filter": has_filter,
    }
    return render(request, "app/sale.html", context)


class SaleCreate(PermissionRequiredMixin, CreateView):
    permission_required = "sellers.can_modify_sale"
    model = Sale
    form_class = SaleForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['seller'] = self.transaction.seller

    #     return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.remittance = get_object_or_404(Remittance, pk=kwargs["pk"])
        # if not self.transaction.modify_sale:
        #     raise Http404
        # add check to determince if user has permission if transaction is in loading stat
        # if self.transaction.status == 'L'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(SaleCreate, self).get_context_data(**kwargs)
        ctx["remittance"] = self.remittance
        return ctx

    def form_valid(self, form):
        form.instance.remittance = self.remittance
        form.instance.is_online = False
        form.instance.status = SALE_STATUS_PROCESSING
        return super(SaleCreate, self).form_valid(form)

    # redirect agad sa pagadd ng order
    def get_success_url(self):
        return reverse("order-create", args=(self.object.id,))


class SaleDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = "sellers.can_access_sale"
    model = Sale

    def get_context_data(self, **kwargs):
        ctx = super(SaleDetail, self).get_context_data(**kwargs)
        ctx["remittance"] = self.object.remittance
        # ctx['access'] = 'order'
        return ctx


class SaleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "sellers.can_modify_sale"
    model = Sale
    form_class = SaleForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['seller'] = self.object.transaction.seller
    #     return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(SaleUpdate, self).get_context_data(**kwargs)
        # if self.object.is_online:
        #     raise Http404
        # ctx['transaction'] = self.object.transaction
        return ctx

    def get_form(self, *args, **kwargs):
        form = super(SaleUpdate, self).get_form(*args, **kwargs)
        if self.object.is_online:
            form.fields["customer"].disabled = True

        return form


class SaleDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "sellers.can_modify_sale"
    model = Sale

    def get_context_data(self, **kwargs):
        ctx = super(SaleDelete, self).get_context_data(**kwargs)
        if self.object.is_online:
            raise Http404
        ctx["remittance"] = self.object.remittance
        return ctx

    def get_success_url(self):
        return reverse("remittance-sale", args=(self.object.remittance.id,))


class SalePayment(PermissionRequiredMixin, UpdateView):
    permission_required = "sellers.can_modify_sale"
    model = Sale
    fields = [
        "payment",
    ]

    def form_valid(self, form):
        form.instance.set_ar()
        return super(SalePayment, self).form_valid(form)


def sale_change_status(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        sale.change_status()
        return redirect("sale-detail", pk=sale.pk)
    context = {"sale": sale}
    return render(request, "app/sale_confirm_change_status.html", context)


def cancel(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    # add to notes the canceled  orders
    if request.method == "POST":
        orders = []
        for order in sale.orders.all():
            orders.append(f"{order} - {order.quantity}")
        notes = (
            "The following was canceled: "
            + " ,".join(orders)
            + ". Sorry for the inconvenience."
        )
        sale.notes = notes
        sale.orders.all().delete()
        sale.status = "C"
        sale.save()
        return redirect("sale-detail", pk=sale.pk)
    context = {"sale": sale}
    return render(request, "app/sale_confirm_cancel.html", context)
