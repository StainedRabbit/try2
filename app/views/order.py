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


from app.models import Sale, Order, User, Product


class OrderForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.inventory = kwargs.pop('inventory', None)
    #     remittance = kwargs.pop('remittance', None)
    #     super(OrderForm, self).__init__(*args, **kwargs)
    #     self.fields['remittance'].initial = remittance

    # remittance = forms.ModelChoiceField(
    #     widget=forms.HiddenInput(), queryset=Remittance.objects.all())

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        product = cleaned_data["product"]
        quantity = (cleaned_data["quantity"] or 0)

        count = product.inventory
        if self.instance.pk:
            count += float(self.instance.quantity)
        else:
            if quantity <= 0:
                raise ValidationError(
                    {"quantity": ValidationError(_("Enter quantity."))}
                )

        # check factor
        if quantity % product.factor != 0:
            raise ValidationError(
                {
                    "quantity": ValidationError(
                        _(f"Quantity is not a factor of {product.factor}.")
                    )
                }
            )

        if quantity > count:
            raise ValidationError({"quantity": ValidationError(_("Out of stock."))})

        discount_quantity = cleaned_data.get("discount_quantity", 0)
        discount_type = cleaned_data.get("discount_type", None)

        if discount_type:
            if not discount_quantity:
                raise ValidationError(
                    {"discount_quantity": ValidationError(_("Enter quantity."))}
                )
        if discount_quantity:
            if not discount_type:
                raise ValidationError(
                    {"discount_type": ValidationError(_("Enter type."))}
                )
        return cleaned_data

    # order_type = forms.ChoiceField(choices=ORDER_TYPE_CHOICE, required=True)

    class Meta:
        model = Order
        fields = ["product", "quantity", "discount_type", "discount_quantity"]
        widgets = {
            "product": autocomplete.ModelSelect2(
                url="product-autocomplete",
            ),
        }


class OrderFilter(django_filters.FilterSet):
    sale__remittance__date = django_filters.DateFromToRangeFilter(
        label="Remittance Date",
        widget=RangeWidget(attrs={"type": "date", "class": "datepicker form-control"}),
    )

    sale__customer = django_filters.ModelChoiceFilter(
        label="Customer",
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="customer-autocomplete",
            forward=(Field("Remittance__seller", "seller"),),
        ),
    )

    product = django_filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="product-all-autocomplete",
            forward=(Field("Remittance__seller", "seller"),),
        ),
    )

    class Meta:
        model = Order
        fields = [
            "sale__remittance__date",
            "sale__id",
            "sale__customer",
            "sale__or_number",
            "product",
        ]


def order(request):
    orders = Order.objects.filter(sale__remittance__is_active=False)
    filter = OrderFilter(request.GET, queryset=orders)
    orders = filter.qs
    has_filter = any(field in request.GET for field in set(filter.get_fields()))
    paginator = Paginator(orders, 10)

    page = request.GET.get("page")
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        "orders": orders,
        "filter": filter,
        "has_filter": has_filter,
    }
    return render(request, "app/order.html", context)


def order_csv(request):
    orders = Order.objects.filter(sale__remittance__is_active=False)
    filter = OrderFilter(request.GET, queryset=orders)
    orders = filter.qs
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)

    writer.writerow(
        [
            "SALE ID",
            "ID",
            "CUSTOMER",
            "OR NUMBER",
            "DATE",
            "PRODUCT",
            "QUANTITY",
            "PRICE",
            "SUBTOTAL",
            "DISCOUNT TYPE",
            "DISCOUNT QUANTITY",
            "DISCOUNT AMOUNT",
            "TOTAL",
        ]
    )

    for order in orders:
        writer.writerow(
            [
                order.sale.id,
                order.id,
                order.sale.customer,
                order.sale.or_number,
                order.sale.created,
                order,
                order.quantity,
                order.price,
                order.sub_total,
                order.get_discount_type_display(),
                order.discount_quantity,
                order.discount_amount,
                order.total,
            ]
        )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="Order - {datetime.date.today()}.csv"'
    return response


class OrderCreate(PermissionRequiredMixin, CreateView):
    permission_required = "sellers.can_modify_sale"
    model = Order
    form_class = OrderForm
    # template_name = 'order_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.sale = get_object_or_404(Sale, pk=kwargs["pk"])
        # online transaction cannot have additional product
        if self.sale.is_online:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(OrderCreate, self).get_context_data(**kwargs)
        ctx["remittance"] = self.sale.remittance
        ctx["sale"] = self.sale
        return ctx

    def form_valid(self, form):
        form.instance.sale = self.sale
        form.instance.price = form.instance.product.price
        return super(OrderCreate, self).form_valid(form)

    # def get_success_url(self):
    #     return reverse('sale-order', args=(self.sale.id,))

    def get_success_url(self):
        messages.success(self.request, f"{self.object} added successfully.")
        return reverse("order-create", args=(self.sale.id,))


class OrderUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "sellers.can_modify_sale"
    model = Order
    form_class = OrderForm

    # def get_form_kwargs(self):
    #     kwargs = super(OrderUpdate, self).get_form_kwargs()
    #     kwargs['inventory'] = self.object.sale.transaction.inventory
    #     kwargs['transaction'] = self.object.sale.transaction
    #     return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(OrderUpdate, self).get_context_data(**kwargs)
        # if self.object.sale.is_online:
        #     raise Http404
        ctx["remittance"] = self.object.sale.remittance
        return ctx

    # def form_valid(self, form):
    #     if self.object.sale.is_online:
    #         # if change in project, include it in the notes
    #         if form.instance.quantity < self.object.quantity:
    #             sale = self.object.sale
    #             notes = f'{self.object} changed from {self.object.quantity} to {form.instance.quantity}. '
    #             notes = sale.notes + notes
    #             sale.notes = notes
    #             sale.save()
    #     return super(OrderUpdate, self).form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super(OrderUpdate, self).get_form(*args, **kwargs)
        if self.object.sale.is_online:
            form.fields["product"].disabled = True
            form.fields["discount_type"].disabled = True
            form.fields["discount_quantity"].disabled = True
            form.fields["quantity"].widget.attrs["max"] = self.object.prev_quantity

        #     inventory = self.object.sale.transaction.inventory
        #     none_zero_id = [product.id for product,
        #                     data in inventory.items() if data[1] > 0]
        #     # add yung product kung zero ang inventory
        #     if inventory[self.object.product][1] <= 0:
        #         none_zero_id.append(self.object.product.id)
        #     form.fields['product'].queryset = Product.for_sale.filter(
        #         id__in=none_zero_id)
        #     form.fields['product'].label_from_instance = lambda obj: f'{obj} | {inventory[obj][0].amount} | {inventory[obj][1]}'
        return form

    def get_success_url(self):
        return reverse("sale-detail", args=(self.object.sale.id,))


class OrderDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "sellers.can_modify_sale"
    model = Order

    def get_context_data(self, **kwargs):
        ctx = super(OrderDelete, self).get_context_data(**kwargs)
        if self.object.sale.is_online:
            raise Http404
        ctx["remittance"] = self.object.sale.remittance
        return ctx

    def get_success_url(self):
        return reverse("sale-detail", args=(self.object.sale.id,))
