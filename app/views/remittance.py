from django_filters.widgets import RangeWidget
from dal import autocomplete
from dal.forward import Field
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


class RemittanceFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(
        label="Date",
        widget=RangeWidget(attrs={"type": "date", "class": "datepicker form-control"}),
    )

    class Meta:
        model = Remittance
        fields = ["date", "with_ar"]


class RemittanceSaleFilter(django_filters.FilterSet):

    customer = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="customer-autocomplete",
            forward=(Field("remittance__seller", "seller"),),
        ),
        # TODO: See how to make this work in case of multiple coop
    )

    class Meta:
        model = Sale
        fields = ["customer", "or_number", "status", "is_ar"]


def remittance_active(request):
    pending_orders = Sale.objects.filter(status="P")
    remittance = Remittance.objects.get(is_active=True)
    context = {
        "pending_orders": pending_orders,
        "remittance": remittance,
    }
    return render(request, "app/remittance_detail.html", context)


def remittance(request):
    remittances = Remittance.objects.filter(is_active=False)
    filter = RemittanceFilter(request.GET, queryset=remittances)
    remittances = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))
    paginator = Paginator(remittances, 10)

    page = request.GET.get("page")
    try:
        remittances = paginator.page(page)
    except PageNotAnInteger:
        remittances = paginator.page(1)
    except EmptyPage:
        remittances = paginator.page(paginator.num_pages)

    context = {
        "remittances": remittances,
        "filter": filter,
        "has_filter": has_filter,
    }
    return render(request, "app/remittance.html", context)


def remittance_csv(request):
    remittances = Remittance.objects.filter(is_active=False)
    filter = RemittanceFilter(request.GET, queryset=remittances)
    remittances = filter.qs
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)

    writer.writerow(
        [
            "ID",
            "DATE",
            "SUBTOTAL",
            "DISCOUNT",
            "TOTAL",
            "PAYMENT",
            "DEBITTED",
            "BALANCE",
            "CASH",
            "COINS",
            "EXPENSES",
            "REMITTANCE",
            "LACK/OVER",
            "NOTES",
        ]
    )

    for remittance in remittances:
        writer.writerow(
            [
                remittance.id,
                remittance.date,
                remittance.sub_total,
                remittance.discount_amount,
                remittance.total,
                remittance.payment_amount,
                remittance.debit_amount,
                remittance.balance,
                remittance.cash,
                remittance.coins,
                remittance.expenses,
                remittance.remitted_amount,
                remittance.lack_over,
                "",
            ]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Remittance - {datetime.date.today()}.csv"'
    return response


def remittance_sale(request, pk):
    remittance = get_object_or_404(Remittance, pk=pk)
    filter = RemittanceSaleFilter(
        request.GET, queryset=remittance.sales.all()
    )  # user=request.user
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
        "remittance": remittance,
        "filter": filter,
        "has_filter": has_filter,
        "sales": sales,
    }
    return render(request, "app/remittance_sale.html", context)


def remittance_sale_csv(request, pk):
    remittance = get_object_or_404(Remittance, pk=pk)
    filter = RemittanceSaleFilter(
        request.GET, queryset=remittance.sales.all()
    )  # user=request.user
    sales = filter.qs
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)
    writer.writerow(
        [
            "SALE ID",
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
                sale.notes,
            ]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Sale Report - {remittance}.csv"'
    return response


# TODO: Add checking of if remittance is inactive
def remittance_remit(request, pk):
    remittance = get_object_or_404(Remittance, pk=pk)
    context = {
        "remittance": remittance,
    }
    return render(request, "app/remittance_remit.html", context)


from django.contrib import messages


def remittance_close(request, pk):
    # TODO: Check all store transaction are completed and online are on for delivery
    remittance = get_object_or_404(Remittance, pk=pk)
    if request.method == "POST":
        remittance.is_active = False
        remittance.date_remitted = datetime.datetime.now()
        remittance.save()

        # create net transaction
        Remittance.objects.create(
            date=datetime.datetime.now() + datetime.timedelta(days=1)
        )

        messages.info(request, "Transaction remitted successfully.")
        return redirect("remittance-active")
    else:
        return render(
            request, "app/remittance_confirm_close.html", {"remittance": remittance}
        )


class RemittanceSaleReport(PermissionRequiredMixin, generic.DetailView):
    permission_required = "sellers.can_access_sale"
    model = Remittance
    template_name = "app/remittance_sale_report.html"


class RemittanceDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = "sellers.can_access_sale"
    model = Remittance


class RemittanceEdit(PermissionRequiredMixin, UpdateView):
    permission_required = "sellers.can_modify_sale"
    model = Remittance
    fields = ["date", "cash", "coins", "expenses"]

    def get_form(self):
        from django.forms.widgets import SelectDateWidget

        form = super().get_form()
        form.fields["date"].widget = SelectDateWidget()
        return form

    def get_success_url(self):
        return reverse("remittance-remit", args=(self.object.id,))
