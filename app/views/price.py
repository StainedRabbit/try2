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


class PriceForm(forms.Form):
    amount = forms.FloatField()


@permission_required("products.can_modify_inventory")
def product_price(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = PriceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            if amount != product.price.amount:
                product.prices.filter(is_active=True).update(is_active=False)
                # check existing price
                price = product.prices.filter(amount=amount).first()
                if price:
                    price.is_active = True
                    price.save()
                else:
                    product.prices.create(
                        amount=amount,
                    )
            url = "%s?%s" % (reverse("product"), request.GET.urlencode())
            return redirect(url)
    else:
        form = PriceForm(
            initial={
                "amount": product.price.amount,
            }
        )
    context = {"product": product, "form": form, "stock": "I"}
    return render(request, "app/price_form.html", context)
