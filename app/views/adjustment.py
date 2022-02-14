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


from app.models import Product


class AdjustmentForm(forms.Form):
    quantity = forms.FloatField()
    notes = forms.CharField(max_length=50, required=False)


def product_adjustment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = AdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = (form.cleaned_data["quantity"] or 0)
            quantity = adjustment - product.inventory
            if quantity:
                product.adjustments.create(
                    quantity=quantity, notes=form.cleaned_data["notes"]
                )
            url = "%s?%s" % (reverse("product"), request.GET.urlencode())
            return redirect(url)
    else:
        form = AdjustmentForm(
            initial={
                "quantity": product.inventory,
            }
        )
    context = {"product": product, "form": form, "stock": "I"}
    return render(request, "app/adjustment_form.html", context)
