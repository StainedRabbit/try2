from app.models import Purchase
from app.models import Procurement
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from dal import autocomplete
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required


class PurchaseForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(PurchaseForm, self).clean()
        product = cleaned_data["product"]
        quantity = (cleaned_data["quantity"] or 0)

        # quantity = product.piece_to_whole(
        #     cleaned_data['whole'], cleaned_data['piece'])

        if quantity <= 0:
            raise ValidationError(_("Enter quantity."))

        # count = self.inventory[product][1]
        # if self.instance.pk:
        #     count += self.instance.quantity
        # if quantity > count:
        #     raise ValidationError(_('Out of stock.'))

        return cleaned_data

    class Meta:
        model = Purchase
        fields = [
            "product",
            "quantity",
            "amount",
        ]
        widgets = {
            "product": autocomplete.ModelSelect2(
                url="product-autocomplete",
            ),
        }


class PurchaseCreate(PermissionRequiredMixin, CreateView):
    permission_required = "products.can_manage_stock"
    model = Purchase
    form_class = PurchaseForm

    def dispatch(self, request, *args, **kwargs):
        self.procurement = get_object_or_404(Procurement, pk=kwargs["pk"])
        if self.procurement.is_done:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # id = self.kwargs.get('pk')
        # procurement = Procurement.objects.get(id=id)
        ctx = super(PurchaseCreate, self).get_context_data(**kwargs)
        ctx["procurement"] = self.procurement
        return ctx

    def form_valid(self, form):
        form.instance.procurement = self.procurement
        return super(PurchaseCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse("procurement-detail", args=(self.procurement.id,))


class PurchaseUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "products.can_manage_stock"
    model = Purchase
    form_class = PurchaseForm

    def get_context_data(self, **kwargs):
        if self.object.procurement.is_done:
            raise Http404
        ctx = super(PurchaseUpdate, self).get_context_data(**kwargs)
        ctx["procurement"] = self.object.procurement
        return ctx

    def get_success_url(self):
        return reverse("procurement-detail", args=(self.object.procurement.id,))


class PurchaseDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "products.can_manage_stock"
    model = Purchase

    def get_context_data(self, **kwargs):
        ctx = super(PurchaseDelete, self).get_context_data(**kwargs)
        if self.object.procurement.is_done:
            raise Http404
        ctx["procurement"] = self.object.procurement
        return ctx

    def get_success_url(self):
        return reverse("procurement-detail", args=(self.object.procurement.id,))
